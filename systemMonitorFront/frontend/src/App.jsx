import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

import LoginForm from "./components/LoginForm";
import NotFound from "./static/NotFound";
import Admin from "./components/Admin";

function App() {
  return (
    <Router>
      <Routes>
        <Route exact path="/" element={<LoginForm />} />
        <Route path="*" element={<NotFound />} />
        <Route path="/Admin" element={<Admin />} />
      </Routes>
    </Router>
  );
}

export default App;
