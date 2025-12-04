import { useState, useEffect } from 'react';
import {
  Box, Typography, Paper, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Chip, Button, Alert, MenuItem, Dialog,
  DialogTitle, DialogContent, DialogActions, TextField
} from '@mui/material';
import { patientAPI } from '../../services/api';

function ViewBills() {
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [paymentDialog, setPaymentDialog] = useState({ open: false, bill: null });
  const [paymentMethod, setPaymentMethod] = useState('Cash');

  useEffect(() => {
    loadBills();
  }, []);

  const loadBills = async () => {
    try {
      const response = await patientAPI.getBills();
      setBills(response.data);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to load bills' });
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = async () => {
    try {
      await patientAPI.payBill(paymentDialog.bill.billid, paymentMethod);
      setMessage({ type: 'success', text: 'Payment processed successfully' });
      setPaymentDialog({ open: false, bill: null });
      setPaymentMethod('Cash');
      loadBills();
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.error || 'Payment failed' });
    }
  };

  const getPaymentStatusColor = (status) => {
    const colors = {
      Paid: 'success',
      Unpaid: 'error',
      Pending: 'warning'
    };
    return colors[status] || 'default';
  };

  const getTotalUnpaid = () => {
    return bills
      .filter(b => b.paymentstatus === 'Unpaid' || b.paymentstatus === 'Pending')
      .reduce((sum, b) => sum + parseFloat(b.amount), 0);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        My Bills
      </Typography>

      {message.text && (
        <Alert severity={message.type} sx={{ mb: 2 }} onClose={() => setMessage({ type: '', text: '' })}>
          {message.text}
        </Alert>
      )}

      <Paper sx={{ p: 2, mb: 2, bgcolor: 'info.light' }}>
        <Typography variant="h6">
          Total Outstanding: Rs. {getTotalUnpaid().toLocaleString()}
        </Typography>
      </Paper>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Bill ID</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Doctor</TableCell>
              <TableCell>Appointment Date</TableCell>
              <TableCell>Amount (PKR)</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Payment Method</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {bills.map((bill) => (
              <TableRow key={bill.billid}>
                <TableCell>{bill.billid}</TableCell>
                <TableCell>{new Date(bill.billdate).toLocaleDateString()}</TableCell>
                <TableCell>{bill.doctorname || '-'}</TableCell>
                <TableCell>
                  {bill.appointmentdatetime
                    ? new Date(bill.appointmentdatetime).toLocaleDateString()
                    : '-'}
                </TableCell>
                <TableCell>
                  <Typography variant="body1" fontWeight="bold">
                    Rs. {parseFloat(bill.amount).toLocaleString()}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={bill.paymentstatus}
                    color={getPaymentStatusColor(bill.paymentstatus)}
                    size="small"
                  />
                </TableCell>
                <TableCell>{bill.paymentmethod || '-'}</TableCell>
                <TableCell>
                  {(bill.paymentstatus === 'Unpaid' || bill.paymentstatus === 'Pending') && (
                    <Button
                      variant="contained"
                      color="success"
                      size="small"
                      onClick={() => setPaymentDialog({ open: true, bill })}
                    >
                      Pay Now
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={paymentDialog.open} onClose={() => setPaymentDialog({ open: false, bill: null })}>
        <DialogTitle>Pay Bill</DialogTitle>
        <DialogContent>
          {paymentDialog.bill && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6" gutterBottom>
                Amount: Rs. {parseFloat(paymentDialog.bill.amount).toLocaleString()}
              </Typography>
              <TextField
                select
                fullWidth
                label="Payment Method"
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value)}
                sx={{ mt: 2 }}
              >
                <MenuItem value="Cash">Cash</MenuItem>
                <MenuItem value="Credit Card">Credit Card</MenuItem>
                <MenuItem value="Debit Card">Debit Card</MenuItem>
                <MenuItem value="Insurance">Insurance</MenuItem>
                <MenuItem value="Online">Online</MenuItem>
                <MenuItem value="Other">Other</MenuItem>
              </TextField>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPaymentDialog({ open: false, bill: null })}>Cancel</Button>
          <Button onClick={handlePayment} variant="contained" color="success">
            Confirm Payment
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default ViewBills;
