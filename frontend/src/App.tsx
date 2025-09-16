import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'

// Placeholder components for now
const Dashboard = () => <div>Dashboard Page</div>
const Login = () => <div>Login Page</div>
const Projects = () => <div>Projects Page</div>
const Tasks = () => <div>Tasks Page</div>

function App() {
  return (
    <Router>
      <div className="app">
        <header className="app-header">
          <h1>TaskFlow</h1>
          <nav>
            <a href="/dashboard">Dashboard</a>
            <a href="/projects">Projects</a>
            <a href="/tasks">Tasks</a>
          </nav>
        </header>

        <main className="app-main">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/login" element={<Login />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/tasks" element={<Tasks />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
