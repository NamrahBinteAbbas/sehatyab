import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip } from '@mui/material';
import { adminAPI } from '../../services/api';

function ViewAllBills() {
  const [bills, setBills] = useState([]);

  useEffect(() => {
    loadBills();
  }, []);

  const loadBills = async () => {
    try {
      const response = await adminAPI.getBills();
      setBills(response.data);
    } catch (error) {
      console.error('Failed to load bills', error);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>All Bills</Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Bill ID</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Patient</TableCell>
              <TableCell>Doctor</TableCell>
              <TableCell>Amount (PKR)</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {bills.map((bill) => (
              <TableRow key={bill.billid}>
                <TableCell>{bill.billid}</TableCell>
                <TableCell>{new Date(bill.billdate).toLocaleDateString()}</TableCell>
                <TableCell>{bill.patientname}</TableCell>
                <TableCell>{bill.doctorname}</TableCell>
                <TableCell>Rs. {parseFloat(bill.amount).toLocaleString()}</TableCell>
                <TableCell><Chip label={bill.paymentstatus} size="small" /></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default ViewAllBills;
