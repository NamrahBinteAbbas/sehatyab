import axios from "axios";

const API_BASE_URL = "/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Auth API
export const authAPI = {
  login: (credentials) => api.post("/auth/login", credentials),
  register: (userData) => api.post("/auth/register", userData),
};

// Patient API
export const patientAPI = {
  getDepartments: () => api.get("/patient/departments"),
  getDoctors: (deptId) =>
    api.get("/patient/doctors", { params: { dept_id: deptId } }),
  getDoctorAvailability: (doctorId, date) =>
    api.get(`/patient/doctor/${doctorId}/availability`, { params: { date } }),
  bookAppointment: (data) => api.post("/patient/appointments/book", data),
  getAppointments: () => api.get("/patient/appointments"),
  cancelAppointment: (id) => api.put(`/patient/appointments/${id}/cancel`),
  rescheduleAppointment: (id, newDatetime) =>
    api.put(`/patient/appointments/${id}/reschedule`, {
      new_datetime: newDatetime,
    }),
  getBills: () => api.get("/patient/bills"),
  payBill: (id, paymentMethod) =>
    api.put(`/patient/bills/${id}/pay`, { payment_method: paymentMethod }),
};

// Admin API
export const adminAPI = {
  addDepartment: (data) => api.post("/admin/departments", data),
  getDepartments: () => api.get("/admin/departments"),
  addRoomType: (data) => api.post("/admin/room-types", data),
  getRoomTypes: () => api.get("/admin/room-types"),
  addRoom: (data) => api.post("/admin/rooms", data),
  getRooms: () => api.get("/admin/rooms"),
  addDoctor: (data) => api.post("/admin/doctors", data),
  addEmployee: (data) => api.post("/admin/employees", data),
  getAppointments: () => api.get("/admin/appointments"),
  getPatients: () => api.get("/admin/patients"),
  getBills: () => api.get("/admin/bills"),
  generateBill: (data) => api.post("/admin/bills/generate", data),
  addDoctorAvailability: (data) => api.post("/admin/doctor-availability", data),
};

// Doctor API
export const doctorAPI = {
  // Get doctor profile
  getProfile: () => api.get("/doctor/profile"),

  // Get appointments (with optional date filter)
  getAppointments: (date) => {
    const params = date ? { date } : {};
    return api.get("/doctor/appointments", { params });
  },

  // Get weekly schedule
  getWeeklySchedule: () => api.get("/doctor/appointments/weekly"),

  // Write or update prescription (with force_overwrite support)
  writePrescription: (
    appointmentId,
    prescriptionText,
    forceOverwrite = false,
  ) =>
    api.put(`/doctor/appointments/${appointmentId}/prescription`, {
      prescription_text: prescriptionText,
      force_overwrite: forceOverwrite,
    }),

  // Get availability
  getAvailability: () => api.get("/doctor/availability"),

  // Add availability
  addAvailability: (availableDate, startTime, endTime) =>
    api.post("/doctor/availability", {
      available_date: availableDate,
      start_time: startTime,
      end_time: endTime,
    }),

  // Update availability (NEW)
  updateAvailability: (availabilityId, data) =>
    api.put(`/doctor/availability/${availabilityId}`, data),

  // Delete availability (NEW)
  deleteAvailability: (availabilityId) =>
    api.delete(`/doctor/availability/${availabilityId}`),

  // Get statistics (NEW)
  getStats: () => api.get("/doctor/stats"),
};

export default api;
