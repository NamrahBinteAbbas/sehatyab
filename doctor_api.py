# doctor_api.py
from flask import Blueprint, jsonify, render_template, request
from datetime import datetime
from db import query_rows, query_value

doctor_bp = Blueprint("doctor", __name__)

# -------------------- CONFIG YOU CAN TWEAK --------------------
# Calendar: how many appointments in one day means "fully booked"?
DAILY_FULLY_BOOKED_THRESHOLD = 8
# Your app currently stores timestamps WITHOUT timezone.
# We'll *treat them as Asia/Karachi local time* when filtering by date.
APP_TZ = "Asia/Karachi"  # purely for SQL conversion below

# -------------------- STATS --------------------
@doctor_bp.get("/api/doctor/<int:doctor_id>/stats")
def doctor_stats(doctor_id: int):
    """
    Returns: { today, week, month, patients }
    All numbers are computed from the 'appointment' table for this doctor.
    """
    # Today (local PKT day). We convert appointmentdatetime to PKT day in SQL.
    sql_today = """
        SELECT COUNT(*)::int
        FROM public.appointment
        WHERE doctorid = %s
          AND (appointmentdatetime AT TIME ZONE %s)::date = (NOW() AT TIME ZONE %s)::date
    """
    today = query_value(sql_today, (doctor_id, APP_TZ, APP_TZ), 0)

    # This week (PKT): date_trunc('week', ...) anchors Monday 00:00 by default.
    sql_week = """
        SELECT COUNT(*)::int
        FROM public.appointment
        WHERE doctorid = %s
          AND (appointmentdatetime AT TIME ZONE %s)
              >= date_trunc('week', (NOW() AT TIME ZONE %s))
          AND (appointmentdatetime AT TIME ZONE %s)
              <  date_trunc('week', (NOW() AT TIME_ZONE %s)) + interval '7 days'
    """
    week = query_value(sql_week, (doctor_id, APP_TZ, APP_TZ, APP_TZ, APP_TZ), 0)

    # This month (PKT): between first day 00:00 and next month 00:00.
    sql_month = """
        WITH base AS (
          SELECT date_trunc('month', (NOW() AT TIME ZONE %s)) AS m0
        )
        SELECT COUNT(*)::int
        FROM public.appointment, base
        WHERE doctorid = %s
          AND (appointmentdatetime AT TIME ZONE %s) >= base.m0
          AND (appointmentdatetime AT TIME ZONE %s) <  base.m0 + interval '1 month'
    """
    month = query_value(sql_month, (APP_TZ, doctor_id, APP_TZ, APP_TZ), 0)

    # Distinct patients seen ever by this doctor (based on appointment rows)
    sql_patients = """
        SELECT COUNT(DISTINCT patientid)::int
        FROM public.appointment
        WHERE doctorid = %s
    """
    patients = query_value(sql_patients, (doctor_id,), 0)

    return jsonify({"today": today, "week": week, "month": month, "patients": patients})

# -------------------- APPOINTMENTS (range) --------------------
@doctor_bp.get("/api/doctor/<int:doctor_id>/appointments")
def doctor_appointments(doctor_id: int):
    """
    Supports optional ?start=ISO&end=ISO (inclusive start, exclusive end).
    Returns a list of rows shaped for the front-end:
      [{ datetime, patient_name, patient_phone, reason, status }, ...]
    """
    # read query params (they come as strings)
    start_s = request.args.get("start")
    end_s   = request.args.get("end")

    # If provided, parse to Python datetimes (still naive). If not, leave None.
    start_dt = _safe_parse_iso(start_s)
    end_dt   = _safe_parse_iso(end_s)

    # We’ll filter in SQL. Your appointmentdatetime is "timestamp without time zone".
    # We'll *treat it as PKT local* by using AT TIME ZONE 'Asia/Karachi' when we need dates.
    # For range filtering by exact instants, we compare as-is (assuming you stored local PKT).
    if start_dt and end_dt:
        sql = """
            SELECT
              a.appointmentdatetime AS datetime,
              p.name  AS patient_name,
              p.contactno AS patient_phone,
              COALESCE(a.prescriptiontext, '') AS reason,
              a.status
            FROM public.appointment a
            JOIN public.patient p ON p.patientid = a.patientid
            WHERE a.doctorid = %s
              AND a.appointmentdatetime >= %s
              AND a.appointmentdatetime <  %s
            ORDER BY a.appointmentdatetime ASC
        """
        params = (doctor_id, start_dt, end_dt)
    else:
        # no range → return next 30 days by default
        sql = """
            SELECT
              a.appointmentdatetime AS datetime,
              p.name  AS patient_name,
              p.contactno AS patient_phone,
              COALESCE(a.prescriptiontext, '') AS reason,
              a.status
            FROM public.appointment a
            JOIN public.patient p ON p.patientid = a.patientid
            WHERE a.doctorid = %s
              AND a.appointmentdatetime >= NOW()::timestamp
              AND a.appointmentdatetime <  (NOW()::timestamp + interval '30 days')
            ORDER BY a.appointmentdatetime ASC
        """
        params = (doctor_id,)

    rows = query_rows(sql, params)

    # Ensure the JSON fields match your front-end exactly.
    # (They already do, thanks to the SELECT aliases.)
    return jsonify(rows)

def _safe_parse_iso(s: str | None):
    if not s:
        return None
    try:
        # Example input: "2025-11-16T00:00:00.000Z" or no "Z".
        # We accept either — Python will parse common forms.
        # We keep it naive (no tz) because your DB column is naive.
        return datetime.fromisoformat(s.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return None

# -------------------- CALENDAR --------------------
@doctor_bp.get("/api/doctor/<int:doctor_id>/calendar")
def doctor_calendar(doctor_id: int):
    """
    Query params: year, month (1..12)
    Returns: { dayNumber: "available"|"partial"|"booked" }
    Logic (simple): count appointments per day.
      0 -> "available"
      1..(threshold-1) -> "partial"
      >= threshold -> "booked"
    """
    try:
        year = int(request.args["year"])
        month = int(request.args["month"])
        assert 1 <= month <= 12
    except Exception:
        return jsonify({"error": "Provide valid year and month"}), 400

    # Month boundaries in SQL (PKT), because your column is naive.
    # We'll count per local PKT day using AT TIME ZONE.
    sql = """
      WITH bounds AS (
        SELECT
          make_timestamp(%s,%s,1,0,0,0) AT TIME ZONE %s AS m0, -- month start in PKT, as timestamp
          (make_timestamp(%s,%s,1,0,0,0) + interval '1 month') AT TIME ZONE %s AS m1
      ),
      daily AS (
        SELECT
          ((a.appointmentdatetime AT TIME ZONE %s)::date) AS day_date,
          COUNT(*)::int AS n
        FROM public.appointment a, bounds
        WHERE a.doctorid = %s
          AND (a.appointmentdatetime AT TIME ZONE %s) >= bounds.m0
          AND (a.appointmentdatetime AT TIME ZONE %s) <  bounds.m1
        GROUP BY 1
      )
      SELECT EXTRACT(day FROM day_date)::int AS day, n
      FROM daily;
    """
    params = (year, month, APP_TZ, year, month, APP_TZ, APP_TZ, doctor_id, APP_TZ, APP_TZ)
    counts = {r["day"]: r["n"] for r in query_rows(sql, params)}

    # Convert counts -> labels
    out = {}
    # figure days in month
    days_in_month = _days_in_month(year, month)
    for d in range(1, days_in_month + 1):
        c = counts.get(d, 0)
        if c == 0:
            out[d] = "available"
        elif c >= DAILY_FULLY_BOOKED_THRESHOLD:
            out[d] = "booked"
        else:
            out[d] = "partial"
    return jsonify(out)

def _days_in_month(y: int, m: int) -> int:
    # quick portable way
    from calendar import monthrange
    return monthrange(y, m)[1]

# -------------------- PAGE ROUTE (unchanged) --------------------
@doctor_bp.get("/doctor")
def doctor_page():
    return render_template("doctor.html")
