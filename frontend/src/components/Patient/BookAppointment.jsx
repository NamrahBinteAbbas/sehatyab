import { useState, useEffect } from 'react';
import {
  Box, Typography, Paper, TextField, Button, MenuItem, Grid,
  Alert, CircularProgress, Card, CardContent, Chip
} from '@mui/material';
import { patientAPI } from '../../services/api';

function BookAppointment() {
  const [departments, setDepartments] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [availability, setAvailability] = useState([]);
  const [selectedDept, setSelectedDept] = useState('');
  const [selectedDoctor, setSelectedDoctor] = useState('');
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTime, setSelectedTime] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    loadDepartments();
  }, []);

  useEffect(() => {
    if (selectedDept) {
      loadDoctors(selectedDept);
    }
  }, [selectedDept]);

  useEffect(() => {
    if (selectedDoctor && selectedDate) {
      loadAvailability(selectedDoctor, selectedDate);
    }
  }, [selectedDoctor, selectedDate]);

  const loadDepartments = async () => {
    try {
      const response = await patientAPI.getDepartments();
      setDepartments(response.data);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to load departments' });
    }
  };

  const loadDoctors = async (deptId) => {
    try {
      const response = await patientAPI.getDoctors(deptId);
      setDoctors(response.data);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to load doctors' });
    }
  };

  const loadAvailability = async (doctorId, date) => {
    try {
      const response = await patientAPI.getDoctorAvailability(doctorId, date);
      setAvailability(response.data);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to load availability' });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const appointmentDateTime = `${selectedDate} ${selectedTime}`;
      await patientAPI.bookAppointment({
        doctor_id: selectedDoctor,
        appointment_datetime: appointmentDateTime
      });
      
      setMessage({ type: 'success', text: 'Appointment booked successfully!' });
      setSelectedDept('');
      setSelectedDoctor('');
      setSelectedDate('');
      setSelectedTime('');
      setAvailability([]);
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.error || 'Failed to book appointment' });
    } finally {
      setLoading(false);
    }
  };

  const getTodayDate = () => {
    return new Date().toISOString().split('T')[0];
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Book Appointment
      </Typography>

      {message.text && (
        <Alert severity={message.type} sx={{ mb: 2 }}>
          {message.text}
        </Alert>
      )}

      <Paper sx={{ p: 3, mt: 2 }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                select
                fullWidth
                label="Select Department"
                value={selectedDept}
                onChange={(e) => {
                  setSelectedDept(e.target.value);
                  setSelectedDoctor('');
                  setDoctors([]);
                }}
                required
              >
                {departments.map((dept) => (
                  <MenuItem key={dept.deptid} value={dept.deptid}>
                    {dept.deptname} - {dept.location}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                select
                fullWidth
                label="Select Doctor"
                value={selectedDoctor}
                onChange={(e) => setSelectedDoctor(e.target.value)}
                disabled={!selectedDept}
                required
              >
                {doctors.map((doctor) => (
                  <MenuItem key={doctor.empid} value={doctor.empid}>
                    {doctor.name} - {doctor.specialization} (Rs. {doctor.consultationfee})
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="date"
                label="Appointment Date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
                inputProps={{ min: getTodayDate() }}
                disabled={!selectedDoctor}
                required
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="time"
                label="Appointment Time"
                value={selectedTime}
                onChange={(e) => setSelectedTime(e.target.value)}
                InputLabelProps={{ shrink: true }}
                disabled={!selectedDate}
                required
              />
            </Grid>

            {availability.length > 0 && (
              <Grid item xs={12}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Doctor Availability
                    </Typography>
                    {availability.map((slot) => (
                      <Box key={slot.availabilityid} sx={{ mb: 1 }}>
                        <Chip
                          label={`${new Date(slot.availabledate).toLocaleDateString()} - ${slot.starttime.substring(0, 5)} to ${slot.endtime.substring(0, 5)}`}
                          color="primary"
                          variant="outlined"
                        />
                      </Box>
                    ))}
                  </CardContent>
                </Card>
              </Grid>
            )}

            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                size="large"
                disabled={loading}
                fullWidth
              >
                {loading ? <CircularProgress size={24} /> : 'Book Appointment'}
              </Button>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Box>
  );
}

export default BookAppointment;
