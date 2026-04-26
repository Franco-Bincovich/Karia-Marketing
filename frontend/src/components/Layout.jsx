import { useState } from "react";
import Sidebar from "./Sidebar";
import Header from "./Header";
import ToastContainer from "./ui/Toast";
import { useViewport } from "../hooks/useViewport";

const SIDEBAR_FULL = 240;
const SIDEBAR_COL = 64;

export default function Layout({ title, children }) {
  const { isMobile, isTablet } = useViewport();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  const sidebarVisible = isMobile ? mobileOpen : true;
  const effectiveCollapsed = isMobile ? false : isTablet ? true : collapsed;
  const sidebarW = effectiveCollapsed ? SIDEBAR_COL : SIDEBAR_FULL;
  const marginLeft = isMobile ? 0 : sidebarW;

  function toggleSidebar() {
    if (isMobile) setMobileOpen((v) => !v);
    else setCollapsed((v) => !v);
  }

  function closeMobile() {
    if (isMobile) setMobileOpen(false);
  }

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "var(--bg)" }}>
      {/* Mobile overlay backdrop */}
      {isMobile && mobileOpen && (
        <div
          onClick={closeMobile}
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.55)",
            backdropFilter: "blur(2px)",
            zIndex: 99,
            animation: "fadeIn 150ms ease",
          }}
        />
      )}

      {/* Sidebar */}
      {sidebarVisible && (
        <Sidebar
          collapsed={effectiveCollapsed}
          onToggle={toggleSidebar}
          onNavigate={closeMobile}
          isMobile={isMobile}
        />
      )}

      {/* Main content */}
      <div
        style={{
          marginLeft,
          flex: 1,
          display: "flex",
          flexDirection: "column",
          minWidth: 0,
          transition: "margin-left var(--t)",
        }}
      >
        <Header title={title} onMenuClick={toggleSidebar} showMenu={isMobile && !mobileOpen} />
        <main
          style={{
            flex: 1,
            padding: isMobile ? "16px 12px 24px" : "24px 28px 32px",
            background: "var(--bg)",
            overflowX: "auto",
            transition: "background var(--t-slow)",
          }}
        >
          {children}
        </main>
      </div>

      {/* Global toast notifications */}
      <ToastContainer />
    </div>
  );
}
