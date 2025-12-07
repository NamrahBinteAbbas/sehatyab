import { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Tooltip,
} from "@mui/material";
import { patientAPI } from "../../services/api";

function ViewAppointments() {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState({ type: "", text: "" });
  const [rescheduleDialog, setRescheduleDialog] = useState({
    open: false,
    appointment: null,
  });
  const [newDateTime, setNewDateTime] = useState({ date: "", time: "" });

  useEffect(() => {
    loadAppointments();
  }, []);

  const loadAppointments = async () => {
    try {
      const response = await patientAPI.getAppointments();
      setAppointments(response.data);
    } catch (error) {
      setMessage({ type: "error", text: "Failed to load appointments" });
    } finally {
      setLoading(false);
    }
  };

  // Format datetime - simple approach treating as PKT
  const formatDateTime = (dateTimeString) => {
    if (!dateTimeString) return "-";

    // Split and parse components
    const [datePart, timePart] = dateTimeString.split("T");
    const [year, month, day] = datePart.split("-");
    const [hours, minutes] = timePart.split(":");

    // Format date
    const monthNames = [
      "Jan",
      "Feb",
      "Mar",
      "Apr",
      "May",
      "Jun",
      "Jul",
      "Aug",
      "Sep",
      "Oct",
      "Nov",
      "Dec",
    ];
    const dateStr = `${monthNames[parseInt(month) - 1]} ${day}, ${year}`;

    // Format time
    const hour12 = parseInt(hours) % 12 || 12;
    const ampm = parseInt(hours) >= 12 ? "PM" : "AM";
    const timeStr = `${hour12}:${minutes} ${ampm}`;

    return `${dateStr}, ${timeStr}`;
  };

  const handleCancel = async (appointmentId) => {
    if (!window.confirm("Are you sure you want to cancel this appointment?"))
      return;

    try {
      await patientAPI.cancelAppointment(appointmentId);
      setMessage({
        type: "success",
        text: "Appointment cancelled successfully",
      });
      loadAppointments();
    } catch (error) {
      setMessage({
        type: "error",
        text: error.response?.data?.error || "Failed to cancel appointment",
      });
    }
  };

  const handleReschedule = async () => {
    if (!newDateTime.date || !newDateTime.time) {
      setMessage({ type: "error", text: "Please select both date and time" });
      return;
    }

    try {
      // Format as ISO string (no timezone)
      const appointmentDateTime = `${newDateTime.date}T${newDateTime.time}:00`;

      await patientAPI.rescheduleAppointment(
        rescheduleDialog.appointment.appointmentid,
        appointmentDateTime,
      );

      setMessage({
        type: "success",
        text: "Appointment rescheduled successfully",
      });
      setRescheduleDialog({ open: false, appointment: null });
      setNewDateTime({ date: "", time: "" });
      loadAppointments();
    } catch (error) {
      setMessage({
        type: "error",
        text: error.response?.data?.error || "Failed to reschedule appointment",
      });
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      Scheduled: "primary",
      Completed: "success",
      Cancelled: "error",
      Rescheduled: "warning",
    };
    return colors[status] || "default";
  };

  const getTodayDate = () => {
    return new Date().toISOString().split("T")[0];
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        My Appointments
      </Typography>

      {message.text && (
        <Alert
          severity={message.type}
          sx={{ mb: 2 }}
          onClose={() => setMessage({ type: "", text: "" })}
        >
          {message.text}
        </Alert>
      )}

      {loading ? (
        <Typography>Loading appointments...</Typography>
      ) : appointments.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: "center" }}>
          <Typography>No appointments found</Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Date & Time</TableCell>
                <TableCell>Doctor</TableCell>
                <TableCell>Specialization</TableCell>
                <TableCell>Department</TableCell>
                <TableCell>Room</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Prescription</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {appointments.map((appointment) => (
                <TableRow key={appointment.appointmentid}>
                  <TableCell>
                    {formatDateTime(appointment.appointmentdatetime)}
                  </TableCell>
                  <TableCell>{appointment.doctorname}</TableCell>
                  <TableCell>{appointment.specialization}</TableCell>
                  <TableCell>{appointment.deptname}</TableCell>
                  <TableCell>{appointment.roomname}</TableCell>
                  <TableCell>
                    <Chip
                      label={appointment.status}
                      color={getStatusColor(appointment.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {appointment.prescriptiontext ? (
                      <Tooltip title={appointment.prescriptiontext}>
                        <Typography
                          variant="body2"
                          sx={{
                            maxWidth: 200,
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                            whiteSpace: "nowrap",
                          }}
                        >
                          {appointment.prescriptiontext}
                        </Typography>
                      </Tooltip>
                    ) : (
                      "-"
                    )}
                  </TableCell>
                  <TableCell>
                    {appointment.status === "Scheduled" && (
                      <>
                        <Button
                          size="small"
                          onClick={() =>
                            setRescheduleDialog({ open: true, appointment })
                          }
                          sx={{ mr: 1 }}
                        >
                          Reschedule
                        </Button>
                        <Button
                          size="small"
                          color="error"
                          onClick={() =>
                            handleCancel(appointment.appointmentid)
                          }
                        >
                          Cancel
                        </Button>
                      </>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Dialog
        open={rescheduleDialog.open}
        onClose={() => {
          setRescheduleDialog({ open: false, appointment: null });
          setNewDateTime({ date: "", time: "" });
        }}
      >
        <DialogTitle>Reschedule Appointment</DialogTitle>
        <DialogContent>
          {rescheduleDialog.appointment && (
            <Box sx={{ mb: 2, mt: 1 }}>
              <Typography variant="body2" color="text.secondary">
                <strong>Current:</strong>{" "}
                {formatDateTime(
                  rescheduleDialog.appointment.appointmentdatetime,
                )}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Doctor:</strong>{" "}
                {rescheduleDialog.appointment.doctorname}
              </Typography>
            </Box>
          )}

          <TextField
            fullWidth
            type="date"
            label="New Date"
            value={newDateTime.date}
            onChange={(e) =>
              setNewDateTime({ ...newDateTime, date: e.target.value })
            }
            InputLabelProps={{ shrink: true }}
            inputProps={{ min: getTodayDate() }}
            sx={{ mt: 2, mb: 2 }}
          />
          <TextField
            fullWidth
            type="time"
            label="New Time"
            value={newDateTime.time}
            onChange={(e) =>
              setNewDateTime({ ...newDateTime, time: e.target.value })
            }
            InputLabelProps={{ shrink: true }}
          />
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setRescheduleDialog({ open: false, appointment: null });
              setNewDateTime({ date: "", time: "" });
            }}
          >
            Cancel
          </Button>
          <Button onClick={handleReschedule} variant="contained">
            Reschedule
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default ViewAppointments;
