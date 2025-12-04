import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip } from '@mui/material';
import { doctorAPI } from '../../services/api';

function ViewSchedule() {
  const [appointments, setAppointments] = useState([]);

  useEffect(() => {
    loadSchedule();
  }, []);

  const loadSchedule = async () => {
    try {
      const response = await doctorAPI.getWeeklySchedule();
      setAppointments(response.data);
    } catch (error) {
      console.error('Failed to load schedule', error);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Weekly Schedule</Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Date & Time</TableCell>
              <TableCell>Patient Name</TableCell>
              <TableCell>Age</TableCell>
              <TableCell>Gender</TableCell>
              <TableCell>Contact</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {appointments.map((appt) => (
              <TableRow key={appt.appointmentid}>
                <TableCell>{new Date(appt.appointmentdatetime).toLocaleString()}</TableCell>
                <TableCell>{appt.patientname}</TableCell>
                <TableCell>{appt.age}</TableCell>
                <TableCell>{appt.gender}</TableCell>
                <TableCell>{appt.contactno}</TableCell>
                <TableCell><Chip label={appt.status} size="small" /></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default ViewSchedule;
