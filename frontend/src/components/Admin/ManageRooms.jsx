import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem, Grid, Alert } from '@mui/material';
import { adminAPI } from '../../services/api';

function ManageRooms() {
  const [rooms, setRooms] = useState([]);
  const [roomTypes, setRoomTypes] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [formData, setFormData] = useState({ type_id: '', room_name: '' });
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [roomsRes, typesRes] = await Promise.all([adminAPI.getRooms(), adminAPI.getRoomTypes()]);
      setRooms(roomsRes.data);
      setRoomTypes(typesRes.data);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to load data' });
    }
  };

  const handleAddRoom = async () => {
    try {
      await adminAPI.addRoom(formData);
      setMessage({ type: 'success', text: 'Room added successfully' });
      setOpenDialog(false);
      setFormData({ type_id: '', room_name: '' });
      loadData();
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.error || 'Failed to add room' });
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Manage Rooms</Typography>
      {message.text && <Alert severity={message.type} sx={{ mb: 2 }}>{message.text}</Alert>}
      <Button variant="contained" onClick={() => setOpenDialog(true)} sx={{ mb: 2 }}>Add Room</Button>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Room Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Total Beds</TableCell>
              <TableCell>Occupied Beds</TableCell>
              <TableCell>Charges/Day (PKR)</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rooms.map((room) => (
              <TableRow key={room.roomid}>
                <TableCell>{room.roomname}</TableCell>
                <TableCell>{room.typename}</TableCell>
                <TableCell>{room.status}</TableCell>
                <TableCell>{room.totalbeds}</TableCell>
                <TableCell>{room.occupiedbeds}</TableCell>
                <TableCell>Rs. {parseFloat(room.chargesperday).toLocaleString()}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>Add Room</DialogTitle>
        <DialogContent>
          <TextField select fullWidth label="Room Type" value={formData.type_id} onChange={(e) => setFormData({ ...formData, type_id: e.target.value })} sx={{ mt: 2, mb: 2 }}>
            {roomTypes.map((type) => (<MenuItem key={type.typeid} value={type.typeid}>{type.typename}</MenuItem>))}
          </TextField>
          <TextField fullWidth label="Room Name" value={formData.room_name} onChange={(e) => setFormData({ ...formData, room_name: e.target.value })} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleAddRoom} variant="contained">Add</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default ManageRooms;
