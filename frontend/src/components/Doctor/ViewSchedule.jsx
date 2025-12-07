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
  Alert,
} from "@mui/material";
import { doctorAPI } from "../../services/api";
import { formatDateTime } from "../../utils/dateFormatter";

function ViewSchedule() {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadSchedule();
  }, []);

  const loadSchedule = async () => {
    try {
      setLoading(true);
      const response = await doctorAPI.getWeeklySchedule();
      console.log("Weekly schedule loaded:", response.data);
      setAppointments(response.data);
      setError("");
    } catch (error) {
      console.error("Failed to load schedule", error);
      setError("Failed to load weekly schedule");
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case "scheduled":
        return "primary";
      case "completed":
        return "success";
      case "cancelled":
        return "error";
      case "rescheduled":
        return "warning";
      default:
        return "default";
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Weekly Schedule
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Paper sx={{ p: 3, textAlign: "center" }}>
          <Typography>Loading schedule...</Typography>
        </Paper>
      ) : appointments.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: "center" }}>
          <Typography>No appointments scheduled for this week</Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Date & Time</TableCell>
                <TableCell>Patient Name</TableCell>
                <TableCell>Age</TableCell>
                <TableCell>Gender</TableCell>
                <TableCell>Contact</TableCell>
                <TableCell>Blood Group</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {appointments.map((appt) => (
                <TableRow key={appt.appointmentid}>
                  <TableCell>
                    {formatDateTime(appt.appointmentdatetime)}
                  </TableCell>
                  <TableCell>{appt.patientname}</TableCell>
                  <TableCell>{appt.age}</TableCell>
                  <TableCell>{appt.gender}</TableCell>
                  <TableCell>{appt.contactno}</TableCell>
                  <TableCell>{appt.bloodgroup || "-"}</TableCell>
                  <TableCell>
                    <Chip
                      label={appt.status}
                      color={getStatusColor(appt.status)}
                      size="small"
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}

export default ViewSchedule;
