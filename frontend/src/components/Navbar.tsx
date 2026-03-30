import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/" className="text-xl font-bold text-blue-600">
          CV Platform
        </Link>
        <div className="flex gap-6 text-sm font-medium text-gray-600">
          <Link to="/dashboard" className="hover:text-blue-600 transition-colors">Dashboard</Link>
          <Link to="/upload" className="hover:text-blue-600 transition-colors">Upload CV</Link>
          <Link to="/jobs" className="hover:text-blue-600 transition-colors">Jobs</Link>
          <Link to="/applications" className="hover:text-blue-600 transition-colors">Applications</Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
