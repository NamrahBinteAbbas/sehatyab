import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import PatientDashboard from './components/Patient/PatientDashboard';
import AdminDashboard from './components/Admin/AdminDashboard';
import DoctorDashboard from './components/Doctor/DoctorDashboard';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    if (token && userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <ThemeProvider theme={theme}>
      <Router>
        <Routes>
          <Route path="/login" element={!user ? <Login setUser={setUser} /> : <Navigate to={`/${user.user_type.toLowerCase()}`} />} />
          <Route path="/register" element={!user ? <Register setUser={setUser} /> : <Navigate to={`/${user.user_type.toLowerCase()}`} />} />
          
          <Route
            path="/patient/*"
            element={user && user.user_type === 'Patient' ? <PatientDashboard user={user} onLogout={handleLogout} /> : <Navigate to="/login" />}
          />
          <Route
            path="/admin/*"
            element={user && user.user_type === 'Admin' ? <AdminDashboard user={user} onLogout={handleLogout} /> : <Navigate to="/login" />}
          />
          <Route
            path="/doctor/*"
            element={user && user.user_type === 'Doctor' ? <DoctorDashboard user={user} onLogout={handleLogout} /> : <Navigate to="/login" />}
          />
          
          <Route path="/" element={<Navigate to="/login" />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
