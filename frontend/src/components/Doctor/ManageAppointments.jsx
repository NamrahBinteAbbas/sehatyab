import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Alert } from '@mui/material';
import { doctorAPI } from '../../services/api';

function ManageAppointments() {
  const [appointments, setAppointments] = useState([]);
  const [prescriptionDialog, setPrescriptionDialog] = useState({ open: false, appointment: null });
  const [prescription, setPrescription] = useState('');
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    loadAppointments();
  }, []);

  const loadAppointments = async () => {
    try {
      const response = await doctorAPI.getAppointments();
      setAppointments(response.data);
    } catch (error) {
      console.error('Failed to load appointments', error);
    }
  };

  const handleWritePrescription = async () => {
    try {
      await doctorAPI.writePrescription(prescriptionDialog.appointment.appointmentid, prescription);
      setMessage({ type: 'success', text: 'Prescription added successfully' });
      setPrescriptionDialog({ open: false, appointment: null });
      setPrescription('');
      loadAppointments();
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to add prescription' });
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Manage Appointments</Typography>
      {message.text && <Alert severity={message.type} sx={{ mb: 2 }}>{message.text}</Alert>}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Date & Time</TableCell>
              <TableCell>Patient</TableCell>
              <TableCell>Age/Gender</TableCell>
              <TableCell>Contact</TableCell>
              <TableCell>Prescription</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {appointments.map((appt) => (
              <TableRow key={appt.appointmentid}>
                <TableCell>{new Date(appt.appointmentdatetime).toLocaleString()}</TableCell>
                <TableCell>{appt.patientname}</TableCell>
                <TableCell>{appt.age} / {appt.gender}</TableCell>
                <TableCell>{appt.contactno}</TableCell>
                <TableCell>{appt.prescriptiontext || '-'}</TableCell>
                <TableCell>
                  {appt.status === 'Scheduled' && (
                    <Button size="small" variant="contained" onClick={() => setPrescriptionDialog({ open: true, appointment: appt })}>
                      Write Prescription
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Dialog open={prescriptionDialog.open} onClose={() => setPrescriptionDialog({ open: false, appointment: null })} maxWidth="md" fullWidth>
        <DialogTitle>Write Prescription</DialogTitle>
        <DialogContent>
          <TextField fullWidth multiline rows={6} label="Prescription" value={prescription} onChange={(e) => setPrescription(e.target.value)} sx={{ mt: 2 }} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPrescriptionDialog({ open: false, appointment: null })}>Cancel</Button>
          <Button onClick={handleWritePrescription} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default ManageAppointments;
