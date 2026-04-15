import { useState } from "react";
import Sidebar from "./Sidebar";
import Header from "./Header";
import { useViewport } from "../hooks/useViewport";

const SIDEBAR_FULL = 224;
const SIDEBAR_COLLAPSED = 64;

export default function Layout({ title, children }) {
  const { isMobile, isTablet } = useViewport();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  const sidebarVisible = isMobile ? mobileOpen : true;
  const effectiveCollapsed = isMobile ? false : (isTablet ? true : collapsed);
  const sidebarW = effectiveCollapsed ? SIDEBAR_COLLAPSED : SIDEBAR_FULL;
  const marginLeft = isMobile ? 0 : sidebarW;

  function toggleSidebar() {
    if (isMobile) setMobileOpen(v => !v);
    else setCollapsed(v => !v);
  }

  function closeMobile() {
    if (isMobile) setMobileOpen(false);
  }

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      {isMobile && mobileOpen && (
        <div
          onClick={closeMobile}
          style={{
            position: "fixed", inset: 0, background: "rgba(0,0,0,.5)",
            zIndex: 99, transition: "opacity 200ms",
          }}
        />
      )}

      {sidebarVisible && (
        <Sidebar
          collapsed={effectiveCollapsed}
          onToggle={toggleSidebar}
          onNavigate={closeMobile}
          isMobile={isMobile}
        />
      )}

      <div style={{
        marginLeft, flex: 1, display: "flex", flexDirection: "column",
        minWidth: 0, transition: "margin-left 200ms",
      }}>
        <Header title={title} onMenuClick={toggleSidebar} showMenu={isMobile && !mobileOpen} />
        <div style={{
          flex: 1,
          padding: isMobile ? "16px 12px" : "24px 28px",
          background: "#F1F5F9",
          overflowX: "auto",
        }}>
          {children}
        </div>
      </div>
    </div>
  );
}
