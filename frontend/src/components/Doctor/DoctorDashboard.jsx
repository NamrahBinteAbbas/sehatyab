import { Routes, Route, Link } from "react-router-dom";
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Box,
  Container,
  Card,
  CardContent,
  Grid,
  Divider,
} from "@mui/material";
import {
  LocalHospital,
  ExitToApp,
  CalendarMonth,
  Assignment,
  Person,
  MedicalServices,
  Room,
} from "@mui/icons-material";
import ViewSchedule from "./ViewSchedule";
import ManageAppointments from "./ManageAppointments";
import { useState, useEffect } from "react";
import { doctorAPI } from "../../services/api";

const drawerWidth = 240;

function DoctorDashboard({ user, onLogout }) {
  const menuItems = [
    { text: "Dashboard", icon: <Person />, path: "/doctor" },
    {
      text: "Weekly Schedule",
      icon: <CalendarMonth />,
      path: "/doctor/schedule",
    },
    {
      text: "Manage Appointments",
      icon: <Assignment />,
      path: "/doctor/appointments",
    },
  ];

  return (
    <Box sx={{ display: "flex" }}>
      <AppBar
        position="fixed"
        sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}
      >
        <Toolbar>
          <LocalHospital sx={{ mr: 2 }} />
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Sehatyaab Hospital - Doctor Portal
          </Typography>
          <Typography variant="body1" sx={{ mr: 2 }}>
            Dr. {user.details?.name || user.username}
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
          "& .MuiDrawer-paper": { width: drawerWidth, boxSizing: "border-box" },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: "auto" }}>
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
  const [profile, setProfile] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [profileRes, statsRes] = await Promise.all([
        doctorAPI.getProfile(),
        doctorAPI.getStats(),
      ]);
      setProfile(profileRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error("Failed to load dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Doctor Dashboard
        </Typography>
        <Typography>Loading...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Doctor Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Profile Card */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <Person sx={{ fontSize: 40, mr: 2, color: "primary.main" }} />
                <Box>
                  <Typography variant="h6">
                    Dr. {profile?.name || user.username}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {profile?.specialization || "General Physician"}
                  </Typography>
                </Box>
              </Box>

              <Divider sx={{ my: 2 }} />

              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <MedicalServices sx={{ mr: 1, color: "text.secondary" }} />
                <Typography variant="body2">
                  <strong>Qualification:</strong>{" "}
                  {profile?.qualification || "MBBS"}
                </Typography>
              </Box>

              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <Room sx={{ mr: 1, color: "text.secondary" }} />
                <Typography variant="body2">
                  <strong>Room:</strong> {profile?.roomname || "Not Assigned"}
                </Typography>
              </Box>

              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <Typography variant="body2">
                  <strong>Department:</strong> {profile?.deptname || "N/A"}
                </Typography>
              </Box>

              <Box sx={{ display: "flex", alignItems: "center" }}>
                <Typography variant="body2">
                  <strong>Consultation Fee:</strong> Rs.{" "}
                  {profile?.consultationfee || 1000}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Stats Card */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Appointment Statistics
              </Typography>

              <Divider sx={{ my: 2 }} />

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Box
                    sx={{
                      textAlign: "center",
                      p: 2,
                      bgcolor: "primary.light",
                      borderRadius: 1,
                    }}
                  >
                    <Typography variant="h4" color="primary.contrastText">
                      {stats?.today_count || 0}
                    </Typography>
                    <Typography variant="body2" color="primary.contrastText">
                      Today
                    </Typography>
                  </Box>
                </Grid>

                <Grid item xs={6}>
                  <Box
                    sx={{
                      textAlign: "center",
                      p: 2,
                      bgcolor: "info.light",
                      borderRadius: 1,
                    }}
                  >
                    <Typography variant="h4" color="info.contrastText">
                      {stats?.tomorrow_count || 0}
                    </Typography>
                    <Typography variant="body2" color="info.contrastText">
                      Tomorrow
                    </Typography>
                  </Box>
                </Grid>

                <Grid item xs={4}>
                  <Box
                    sx={{
                      textAlign: "center",
                      p: 2,
                      bgcolor: "warning.light",
                      borderRadius: 1,
                    }}
                  >
                    <Typography variant="h4">
                      {stats?.scheduled_count || 0}
                    </Typography>
                    <Typography variant="body2">Scheduled</Typography>
                  </Box>
                </Grid>

                <Grid item xs={4}>
                  <Box
                    sx={{
                      textAlign: "center",
                      p: 2,
                      bgcolor: "success.light",
                      borderRadius: 1,
                    }}
                  >
                    <Typography variant="h4">
                      {stats?.completed_count || 0}
                    </Typography>
                    <Typography variant="body2">Completed</Typography>
                  </Box>
                </Grid>

                <Grid item xs={4}>
                  <Box
                    sx={{
                      textAlign: "center",
                      p: 2,
                      bgcolor: "error.light",
                      borderRadius: 1,
                    }}
                  >
                    <Typography variant="h4">
                      {stats?.cancelled_count || 0}
                    </Typography>
                    <Typography variant="body2">Cancelled</Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default DoctorDashboard;
