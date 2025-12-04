import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip } from '@mui/material';
import { adminAPI } from '../../services/api';

function ViewAllAppointments() {
  const [appointments, setAppointments] = useState([]);

  useEffect(() => {
    loadAppointments();
  }, []);

  const loadAppointments = async () => {
    try {
      const response = await adminAPI.getAppointments();
      setAppointments(response.data);
    } catch (error) {
      console.error('Failed to load appointments', error);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>All Appointments</Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Date & Time</TableCell>
              <TableCell>Patient</TableCell>
              <TableCell>Doctor</TableCell>
              <TableCell>Department</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {appointments.map((appt) => (
              <TableRow key={appt.appointmentid}>
                <TableCell>{new Date(appt.appointmentdatetime).toLocaleString()}</TableCell>
                <TableCell>{appt.patientname}</TableCell>
                <TableCell>{appt.doctorname} - {appt.specialization}</TableCell>
                <TableCell>{appt.deptname}</TableCell>
                <TableCell><Chip label={appt.status} size="small" /></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default ViewAllAppointments;
