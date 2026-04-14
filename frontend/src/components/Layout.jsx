import Sidebar from "./Sidebar";
import Header from "./Header";

const s = {
  wrapper: { display: "flex", minHeight: "100vh" },
  main: { marginLeft: 224, flex: 1, display: "flex", flexDirection: "column" },
  content: { flex: 1, padding: "24px 28px", background: "#F1F5F9" },
};

export default function Layout({ title, children }) {
  return (
    <div style={s.wrapper}>
      <Sidebar />
      <div style={s.main}>
        <Header title={title} />
        <div style={s.content}>{children}</div>
      </div>
    </div>
  );
}
