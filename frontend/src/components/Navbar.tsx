import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "./AuthContext";

const NAV_LINKS = [
  { to: "/", label: "Dashboard" },
  { to: "/cvs", label: "CVs" },
  { to: "/jobs", label: "Jobs" },
  { to: "/match", label: "Match" },
  { to: "/tailor", label: "Tailor" },
  { to: "/cover-letters", label: "Cover Letters" },
  { to: "/applications", label: "Applications" },
  { to: "/search", label: "Search" },
  { to: "/coaching", label: "Coaching" },
  { to: "/analytics", label: "Analytics" },
  { to: "/gdpr", label: "Privacy" },
];

const Navbar = () => {
  const { token, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/" className="text-lg font-bold text-blue-600 shrink-0">
          CV Platform
        </Link>
        {token && (
          <div className="flex items-center gap-1 overflow-x-auto text-xs font-medium text-gray-600 flex-1 mx-4">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className="hover:text-blue-600 transition-colors whitespace-nowrap px-2 py-1 rounded hover:bg-gray-50"
              >
                {link.label}
              </Link>
            ))}
          </div>
        )}
        {token ? (
          <button onClick={handleLogout} className="text-xs text-gray-500 hover:text-red-600 shrink-0">
            Logout
          </button>
        ) : (
          <Link to="/login" className="text-xs text-blue-600 font-medium">Sign in</Link>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
