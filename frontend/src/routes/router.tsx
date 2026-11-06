import { createBrowserRouter, Navigate } from "react-router-dom";

import { ProtectedRoute } from "../auth/ProtectedRoute";
import { CandidatesPage } from "../features/candidates/CandidatesPage";
import { JobDetailPage } from "../features/jobs/JobDetailPage";
import { JobsPage } from "../features/jobs/JobsPage";
import { AppLayout } from "../layouts/AppLayout";
import { LoginPage } from "../pages/LoginPage";
import { RegisterPage } from "../pages/RegisterPage";

export const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  { path: "/register", element: <RegisterPage /> },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { path: "/", element: <Navigate to="/jobs" replace /> },
          { path: "/jobs", element: <JobsPage /> },
          { path: "/jobs/:id", element: <JobDetailPage /> },
          { path: "/candidates", element: <CandidatesPage /> },
        ],
      },
    ],
  },
  { path: "*", element: <Navigate to="/" replace /> },
]);
