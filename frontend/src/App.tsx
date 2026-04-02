import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./components/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminRoute from "./components/AdminRoute";
import Navbar from "./components/Navbar";

import Admin from "./pages/Admin";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import CVs from "./pages/CVs";
import Jobs from "./pages/Jobs";
import Match from "./pages/Match";
import Tailor from "./pages/Tailor";
import CoverLetters from "./pages/CoverLetters";
import Applications from "./pages/Applications";
import Search from "./pages/Search";
import Coaching from "./pages/Coaching";
import Analytics from "./pages/Analytics";
import GDPR from "./pages/GDPR";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-50">
          <Navbar />
          <main className="max-w-6xl mx-auto px-4">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="/cvs" element={<ProtectedRoute><CVs /></ProtectedRoute>} />
              <Route path="/jobs" element={<ProtectedRoute><Jobs /></ProtectedRoute>} />
              <Route path="/match" element={<ProtectedRoute><Match /></ProtectedRoute>} />
              <Route path="/tailor" element={<ProtectedRoute><Tailor /></ProtectedRoute>} />
              <Route path="/cover-letters" element={<ProtectedRoute><CoverLetters /></ProtectedRoute>} />
              <Route path="/applications" element={<ProtectedRoute><Applications /></ProtectedRoute>} />
              <Route path="/search" element={<ProtectedRoute><Search /></ProtectedRoute>} />
              <Route path="/coaching" element={<ProtectedRoute><Coaching /></ProtectedRoute>} />
              <Route path="/analytics" element={<ProtectedRoute><Analytics /></ProtectedRoute>} />
              <Route path="/gdpr" element={<ProtectedRoute><GDPR /></ProtectedRoute>} />
              <Route path="/admin" element={<AdminRoute><Admin /></AdminRoute>} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
