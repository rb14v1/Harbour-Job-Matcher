import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";

export function AppLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-header-title">Job Matcher</div>
        <nav className="app-nav">
          <NavLink to="/jobs" end>Job Postings</NavLink>
          <NavLink to="/candidates">Candidates</NavLink>
        </nav>
        <div className="app-header-user">
          <span>{user?.email}</span>
          <button onClick={logout}>Log out</button>
        </div>
      </header>
      <main className="app-content">
        <Outlet />
      </main>
    </div>
  );
}
