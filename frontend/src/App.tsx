import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import Home from "./pages/Home";
import Category from "./pages/Category";
import Model from "./pages/Model";
import Models from "./pages/Models";
import Installed from "./pages/Installed";
import Jobs from "./pages/Jobs";
import JobDetail from "./pages/JobDetail";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="c/:catId" element={<Category />} />
        <Route path="m/:modelId" element={<Model />} />
        <Route path="models" element={<Models />} />
        <Route path="installed" element={<Installed />} />
        <Route path="jobs" element={<Jobs />} />
        <Route path="jobs/:jobId" element={<JobDetail />} />
      </Route>
    </Routes>
  );
}
