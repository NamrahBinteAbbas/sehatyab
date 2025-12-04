import { useState, useEffect } from 'react';
import {
  Box, Typography, Paper, TextField, Button, MenuItem, Grid, Alert
} from '@mui/material';
import { adminAPI } from '../../services/api';

function AddDoctor() {
  const [departments, setDepartments] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    name: '',
    gender: '',
    contact: '',
    salary: '',
    dept_id: '',
    specialization: '',
    qualification: '',
    room_id: '',
    consultation_fee: '1000'
  });
  const [message, setMessage] = useState({ type: '', text: '' });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [deptRes, roomRes] = await Promise.all([
        adminAPI.getDepartments(),
        adminAPI.getRooms()
      ]);
      setDepartments(deptRes.data);
      setRooms(roomRes.data.filter(r => r.bedsperroom === 0));
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to load data' });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      await adminAPI.addDoctor({
        ...formData,
        salary: parseFloat(formData.salary),
        consultation_fee: parseFloat(formData.consultation_fee),
        dept_id: formData.dept_id || null,
        room_id: formData.room_id || null
      });
      
      setMessage({ type: 'success', text: 'Doctor added successfully!' });
      setFormData({
        username: '', email: '', password: '', name: '', gender: '',
        contact: '', salary: '', dept_id: '', specialization: '',
        qualification: '', room_id: '', consultation_fee: '1000'
      });
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.error || 'Failed to add doctor' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Add Doctor
      </Typography>

      {message.text && (
        <Alert severity={message.type} sx={{ mb: 2 }}>
          {message.text}
        </Alert>
      )}

      <Paper sx={{ p: 3, mt: 2 }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Username"
                required
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Password"
                type="password"
                required
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Full Name"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Gender"
                required
                value={formData.gender}
                onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
              >
                <MenuItem value="Male">Male</MenuItem>
                <MenuItem value="Female">Female</MenuItem>
                <MenuItem value="Other">Other</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Contact"
                required
                value={formData.contact}
                onChange={(e) => setFormData({ ...formData, contact: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Salary (PKR)"
                type="number"
                required
                value={formData.salary}
                onChange={(e) => setFormData({ ...formData, salary: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Department"
                value={formData.dept_id}
                onChange={(e) => setFormData({ ...formData, dept_id: e.target.value })}
              >
                {departments.map((dept) => (
                  <MenuItem key={dept.deptid} value={dept.deptid}>
                    {dept.deptname}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Specialization"
                required
                value={formData.specialization}
                onChange={(e) => setFormData({ ...formData, specialization: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Qualification"
                required
                value={formData.qualification}
                onChange={(e) => setFormData({ ...formData, qualification: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Consultation Room"
                value={formData.room_id}
                onChange={(e) => setFormData({ ...formData, room_id: e.target.value })}
              >
                {rooms.map((room) => (
                  <MenuItem key={room.roomid} value={room.roomid}>
                    {room.roomname} ({room.typename})
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Consultation Fee (PKR)"
                type="number"
                required
                value={formData.consultation_fee}
                onChange={(e) => setFormData({ ...formData, consultation_fee: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                size="large"
                disabled={loading}
                fullWidth
              >
                {loading ? 'Adding Doctor...' : 'Add Doctor'}
              </Button>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Box>
  );
}

export default AddDoctor;
