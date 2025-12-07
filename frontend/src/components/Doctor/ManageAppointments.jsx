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
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Chip,
  IconButton,
  Tooltip,
  FormControlLabel,
  Checkbox,
} from "@mui/material";
import { Edit as EditIcon, Visibility as ViewIcon } from "@mui/icons-material";
import { doctorAPI } from "../../services/api";
import {
  formatDateTime,
  hasDateTimePassed,
  getTimeStatus,
} from "../../utils/dateFormatter";

function ManageAppointments() {
  const [appointments, setAppointments] = useState([]);
  const [prescriptionDialog, setPrescriptionDialog] = useState({
    open: false,
    appointment: null,
  });
  const [prescription, setPrescription] = useState("");
  const [forceOverwrite, setForceOverwrite] = useState(false);
  const [message, setMessage] = useState({ type: "", text: "" });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadAppointments();
  }, []);

  const loadAppointments = async () => {
    try {
      setLoading(true);
      const response = await doctorAPI.getAppointments();
      console.log("Appointments loaded:", response.data);
      setAppointments(response.data);
      setMessage({ type: "", text: "" });
    } catch (error) {
      console.error("Failed to load appointments", error);
      setMessage({
        type: "error",
        text: error.response?.data?.error || "Failed to load appointments",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleOpenPrescriptionDialog = (appt) => {
    console.log("Opening dialog for appointment:", appt);
    setPrescriptionDialog({ open: true, appointment: appt });
    setPrescription(appt.prescriptiontext || "");
    setForceOverwrite(false);
  };

  const handleWritePrescription = async () => {
    if (!prescription.trim()) {
      setMessage({ type: "error", text: "Prescription text cannot be empty" });
      return;
    }

    try {
      setLoading(true);
      await doctorAPI.writePrescription(
        prescriptionDialog.appointment.appointmentid,
        prescription,
        forceOverwrite,
      );

      setMessage({ type: "success", text: "Prescription added successfully" });
      setPrescriptionDialog({ open: false, appointment: null });
      setPrescription("");
      setForceOverwrite(false);
      loadAppointments();
    } catch (error) {
      const errorMsg =
        error.response?.data?.error || "Failed to add prescription";
      const existingPrescription = error.response?.data?.existing_prescription;

      if (error.response?.status === 409 && existingPrescription) {
        setMessage({
          type: "warning",
          text: 'Prescription already exists. Check "Overwrite" to update it.',
        });
      } else {
        setMessage({ type: "error", text: errorMsg });
      }
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
        Manage Appointments
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

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Date & Time</TableCell>
              <TableCell>Patient</TableCell>
              <TableCell>Age/Gender</TableCell>
              <TableCell>Contact</TableCell>
              <TableCell>Blood Group</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Prescription</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading && appointments.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  Loading appointments...
                </TableCell>
              </TableRow>
            ) : appointments.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  No appointments found
                </TableCell>
              </TableRow>
            ) : (
              appointments.map((appt) => {
                // Use utility functions from dateFormatter.js
                const timeStatus = getTimeStatus(appt.appointmentdatetime);
                const canWrite = hasDateTimePassed(appt.appointmentdatetime);

                return (
                  <TableRow key={appt.appointmentid}>
                    <TableCell>
                      <Box>
                        <Typography variant="body2">
                          {formatDateTime(appt.appointmentdatetime)}
                        </Typography>
                        {(appt.status === "Scheduled" ||
                          appt.status === "Rescheduled") && (
                          <Typography variant="caption" color="text.secondary">
                            {timeStatus.message}
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>{appt.patientname}</TableCell>
                    <TableCell>
                      {appt.age} / {appt.gender}
                    </TableCell>
                    <TableCell>{appt.contactno}</TableCell>
                    <TableCell>{appt.bloodgroup || "-"}</TableCell>
                    <TableCell>
                      <Chip
                        label={appt.status}
                        color={getStatusColor(appt.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {appt.prescriptiontext ? (
                        <Tooltip title={appt.prescriptiontext}>
                          <Typography
                            variant="body2"
                            sx={{
                              maxWidth: 200,
                              overflow: "hidden",
                              textOverflow: "ellipsis",
                              whiteSpace: "nowrap",
                            }}
                          >
                            {appt.prescriptiontext}
                          </Typography>
                        </Tooltip>
                      ) : (
                        "-"
                      )}
                    </TableCell>
                    <TableCell>
                      {/* Show button for Scheduled OR Rescheduled appointments */}
                      {(appt.status === "Scheduled" ||
                        appt.status === "Rescheduled") &&
                        canWrite && (
                          <Tooltip
                            title={
                              appt.prescriptiontext
                                ? "Edit prescription"
                                : "Write prescription"
                            }
                          >
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => handleOpenPrescriptionDialog(appt)}
                            >
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                        )}
                      {(appt.status === "Scheduled" ||
                        appt.status === "Rescheduled") &&
                        !canWrite && (
                          <Tooltip title="Prescription can only be written during or after appointment time">
                            <span>
                              <IconButton size="small" disabled>
                                <EditIcon />
                              </IconButton>
                            </span>
                          </Tooltip>
                        )}
                      {appt.status === "Completed" && appt.prescriptiontext && (
                        <Tooltip title="View prescription">
                          <IconButton
                            size="small"
                            color="info"
                            onClick={() => handleOpenPrescriptionDialog(appt)}
                          >
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog
        open={prescriptionDialog.open}
        onClose={() => {
          setPrescriptionDialog({ open: false, appointment: null });
          setPrescription("");
          setForceOverwrite(false);
        }}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {prescriptionDialog.appointment?.prescriptiontext
            ? "Edit Prescription"
            : "Write Prescription"}
        </DialogTitle>
        <DialogContent>
          {prescriptionDialog.appointment && (
            <Box sx={{ mb: 2, mt: 1 }}>
              <Typography variant="body2" color="text.secondary">
                <strong>Patient:</strong>{" "}
                {prescriptionDialog.appointment.patientname}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Age/Gender:</strong>{" "}
                {prescriptionDialog.appointment.age} /{" "}
                {prescriptionDialog.appointment.gender}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Appointment:</strong>{" "}
                {formatDateTime(
                  prescriptionDialog.appointment.appointmentdatetime,
                )}
              </Typography>
            </Box>
          )}

          <TextField
            fullWidth
            multiline
            rows={8}
            label="Prescription"
            placeholder="Enter prescription details..."
            value={prescription}
            onChange={(e) => setPrescription(e.target.value)}
            disabled={prescriptionDialog.appointment?.status === "Completed"}
            sx={{ mt: 2 }}
          />

          {prescriptionDialog.appointment?.prescriptiontext && (
            <FormControlLabel
              control={
                <Checkbox
                  checked={forceOverwrite}
                  onChange={(e) => setForceOverwrite(e.target.checked)}
                />
              }
              label="Overwrite existing prescription"
              sx={{ mt: 2 }}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setPrescriptionDialog({ open: false, appointment: null });
              setPrescription("");
              setForceOverwrite(false);
            }}
          >
            Cancel
          </Button>
          {prescriptionDialog.appointment?.status !== "Completed" && (
            <Button
              onClick={handleWritePrescription}
              variant="contained"
              disabled={loading || !prescription.trim()}
            >
              {loading ? "Saving..." : "Save Prescription"}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default ManageAppointments;
