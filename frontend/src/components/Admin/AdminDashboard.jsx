import { Routes, Route, Link } from 'react-router-dom';
import {
  AppBar, Toolbar, Typography, Button, Drawer, List, ListItem,
  ListItemIcon, ListItemText, Box, Container
} from '@mui/material';
import {
  LocalHospital, ExitToApp, Person, Group, MeetingRoom,
  CalendarMonth, Receipt, Assessment
} from '@mui/icons-material';
import AddDoctor from './AddDoctor';
import ManageRooms from './ManageRooms';
import ViewAllAppointments from './ViewAllAppointments';
import ViewAllBills from './ViewAllBills';
import ViewAllPatients from './ViewAllPatients';

const drawerWidth = 240;

function AdminDashboard({ user, onLogout }) {
  const menuItems = [
    { text: 'Add Doctor', icon: <Person />, path: '/admin/add-doctor' },
    { text: 'Manage Rooms', icon: <MeetingRoom />, path: '/admin/rooms' },
    { text: 'All Appointments', icon: <CalendarMonth />, path: '/admin/appointments' },
    { text: 'All Bills', icon: <Receipt />, path: '/admin/bills' },
    { text: 'All Patients', icon: <Group />, path: '/admin/patients' },
  ];

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <LocalHospital sx={{ mr: 2 }} />
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Sehatyaab Hospital - Admin Portal
          </Typography>
          <Typography variant="body1" sx={{ mr: 2 }}>
            {user.details?.name || user.username}
          </Typography>
          <Button color="inherit" onClick={onLogout} startIcon={<ExitToApp />}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': { width: drawerWidth, boxSizing: 'border-box' },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto' }}>
          <List>
            {menuItems.map((item) => (
              <ListItem button key={item.text} component={Link} to={item.path}>
                <ListItemIcon>{item.icon}</ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar />
        <Container maxWidth="lg">
          <Routes>
            <Route path="/" element={<AdminHome user={user} />} />
            <Route path="/add-doctor" element={<AddDoctor />} />
            <Route path="/rooms" element={<ManageRooms />} />
            <Route path="/appointments" element={<ViewAllAppointments />} />
            <Route path="/bills" element={<ViewAllBills />} />
            <Route path="/patients" element={<ViewAllPatients />} />
          </Routes>
        </Container>
      </Box>
    </Box>
  );
}

function AdminHome({ user }) {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Admin Dashboard
      </Typography>
      <Typography variant="body1" paragraph>
        Welcome, {user.details?.name || user.username}!
      </Typography>
      <Typography variant="body1">
        Use the menu on the left to manage hospital operations.
      </Typography>
    </Box>
  );
}

export default AdminDashboard;
