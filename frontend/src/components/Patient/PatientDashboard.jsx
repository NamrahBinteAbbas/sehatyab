import { useState } from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import {
  AppBar, Toolbar, Typography, Button, Drawer, List, ListItem,
  ListItemIcon, ListItemText, Box, Container
} from '@mui/material';
import {
  Event, LocalHospital, Receipt, ExitToApp, CalendarMonth
} from '@mui/icons-material';
import BookAppointment from './BookAppointment';
import ViewAppointments from './ViewAppointments';
import ViewBills from './ViewBills';

const drawerWidth = 240;

function PatientDashboard({ user, onLogout }) {
  const navigate = useNavigate();

  const menuItems = [
    { text: 'Book Appointment', icon: <Event />, path: '/patient/book' },
    { text: 'My Appointments', icon: <CalendarMonth />, path: '/patient/appointments' },
    { text: 'My Bills', icon: <Receipt />, path: '/patient/bills' },
  ];

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <LocalHospital sx={{ mr: 2 }} />
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Sehatyaab Hospital - Patient Portal
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
            <Route path="/" element={<DashboardHome user={user} />} />
            <Route path="/book" element={<BookAppointment />} />
            <Route path="/appointments" element={<ViewAppointments />} />
            <Route path="/bills" element={<ViewBills />} />
          </Routes>
        </Container>
      </Box>
    </Box>
  );
}

function DashboardHome({ user }) {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Welcome, {user.details?.name || user.username}!
      </Typography>
      <Typography variant="body1" paragraph>
        Patient ID: {user.details?.patientid}
      </Typography>
      <Typography variant="body1" paragraph>
        Use the menu on the left to book appointments, view your medical history, and manage your bills.
      </Typography>
    </Box>
  );
}

export default PatientDashboard;
