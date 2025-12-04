import { Routes, Route, Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Button, Drawer, List, ListItem, ListItemIcon, ListItemText, Box, Container } from '@mui/material';
import { LocalHospital, ExitToApp, CalendarMonth, Assignment } from '@mui/icons-material';
import ViewSchedule from './ViewSchedule';
import ManageAppointments from './ManageAppointments';

const drawerWidth = 240;

function DoctorDashboard({ user, onLogout }) {
  const menuItems = [
    { text: 'Weekly Schedule', icon: <CalendarMonth />, path: '/doctor/schedule' },
    { text: 'Manage Appointments', icon: <Assignment />, path: '/doctor/appointments' },
  ];

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <LocalHospital sx={{ mr: 2 }} />
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Sehatyaab Hospital - Doctor Portal
          </Typography>
          <Typography variant="body1" sx={{ mr: 2 }}>{user.details?.name || user.username}</Typography>
          <Button color="inherit" onClick={onLogout} startIcon={<ExitToApp />}>Logout</Button>
        </Toolbar>
      </AppBar>
      <Drawer variant="permanent" sx={{ width: drawerWidth, flexShrink: 0, '& .MuiDrawer-paper': { width: drawerWidth, boxSizing: 'border-box' } }}>
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
            <Route path="/" element={<DoctorHome user={user} />} />
            <Route path="/schedule" element={<ViewSchedule />} />
            <Route path="/appointments" element={<ManageAppointments />} />
          </Routes>
        </Container>
      </Box>
    </Box>
  );
}

function DoctorHome({ user }) {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>Doctor Dashboard</Typography>
      <Typography variant="body1" paragraph>Welcome, Dr. {user.details?.name || user.username}!</Typography>
      <Typography variant="body1">Specialization: {user.details?.specialization}</Typography>
    </Box>
  );
}

export default DoctorDashboard;
