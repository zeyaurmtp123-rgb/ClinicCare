
"use client";

import { useState } from "react";

export default function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("PATIENT");
  const [specialization, setSpecialization] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleRegister(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setMessage("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name,
          email,
          password,
          role,
          specialization: role === "DOCTOR" ? specialization : null,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : JSON.stringify(data.detail || data)
        );
      }

      setMessage("Registration successful! You can now log in.");
    } catch (error) {
      setMessage(
        error instanceof Error ? error.message : "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-blue-50 px-4 py-10">
      <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-lg">
        <h1 className="mb-2 text-center text-3xl font-bold text-blue-700">
          ClinicCare
        </h1>

        <h2 className="mb-6 text-center text-2xl font-semibold text-gray-800">
          Create Account
        </h2>

        <form onSubmit={handleRegister} className="space-y-4">
          <div>
            <label className="mb-2 block text-gray-700">Full Name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              placeholder="Enter your name"
              className="w-full rounded-lg border p-3 text-gray-800"
            />
          </div>

          <div>
            <label className="mb-2 block text-gray-700">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="Enter your email"
              className="w-full rounded-lg border p-3 text-gray-800"
            />
          </div>

          <div>
            <label className="mb-2 block text-gray-700">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Create a password"
              className="w-full rounded-lg border p-3 text-gray-800"
            />
          </div>

          <div>
            <label className="mb-2 block text-gray-700">Register As</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full rounded-lg border p-3 text-gray-800"
            >
              <option value="PATIENT">Patient</option>
              <option value="DOCTOR">Doctor</option>
            </select>
          </div>

          {role === "DOCTOR" && (
            <div>
              <label className="mb-2 block text-gray-700">
                Specialization
              </label>
              <input
                value={specialization}
                onChange={(e) => setSpecialization(e.target.value)}
                required
                placeholder="e.g. General"
                className="w-full rounded-lg border p-3 text-gray-800"
              />
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-blue-600 py-3 font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Registering..." : "Register"}
          </button>
        </form>

        {message && (
          <p className="mt-4 text-center text-sm text-blue-700">
            {message}
          </p>
        )}

        <p className="mt-5 text-center text-gray-600">
          Already have an account?{" "}
          <a href="/login" className="font-semibold text-blue-600">
            Login
          </a>
        </p>

        <p className="mt-4 text-center">
          <a href="/" className="text-sm text-gray-500">
            Back to Home
          </a>
        </p>
      </div>
    </main>
  );
}
