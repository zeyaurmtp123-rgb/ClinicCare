
"use client";

import { useEffect, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";

const API = "http://127.0.0.1:8000";

type Slot = {
  slot_id: number;
  start_time: string;
  end_time: string;
};

type Doctor = {
  doctor_id: number;
  name: string;
  specialization: string;
  available_slots?: Slot[];
};

type PatientAppointment = {
  appointment_id: number;
  slot_id: number;
  doctor_name: string;
  specialization: string;
  start_time: string;
  end_time: string;
  status: string;
};

type DoctorAppointment = {
  appointment_id: number;
  patient_name: string;
  doctor_name: string;
  start_time: string;
  end_time: string;
  status: string;
};

type WeeklyReportItem = {
  status: string;
  appointment_count: number;
};

function todayLocalDate() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function formatDate(value: string) {
  return new Date(value).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function formatTime(value: string) {
  return new Date(value).toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function statusStyle(status: string) {
  const s = status.toUpperCase();

  if (s === "BOOKED") return { background: "#dbeafe", color: "#1d4ed8" };
  if (s === "COMPLETED") return { background: "#dcfce7", color: "#15803d" };
  if (s === "CANCELLED") return { background: "#fee2e2", color: "#b91c1c" };
  if (s === "NO_SHOW") return { background: "#fef3c7", color: "#92400e" };

  return { background: "#f1f5f9", color: "#475569" };
}

export default function Dashboard() {
  const router = useRouter();

  const [role, setRole] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState<"success" | "error">("success");

  const [specialization, setSpecialization] = useState("General");
  const [searchDate, setSearchDate] = useState("");
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [appointments, setAppointments] = useState<PatientAppointment[]>([]);
  const [doctorAppointments, setDoctorAppointments] = useState<DoctorAppointment[]>([]);

  const [weeklyReport, setWeeklyReport] = useState<WeeklyReportItem[]>([]);
  const [todayDate, setTodayDate] = useState("");
  const [nowTimestamp, setNowTimestamp] = useState(0);

  const [slotStart, setSlotStart] = useState("");
  const [slotEnd, setSlotEnd] = useState("");
  const [deleteSlotId, setDeleteSlotId] = useState("");
  const [rescheduleSlots, setRescheduleSlots] = useState<Record<number, string>>({});

  function token() {
    return sessionStorage.getItem("access_token");
  }

  async function request(path: string, options: RequestInit = {}) {
    const response = await fetch(`${API}${path}`, {
      ...options,
      headers: {
        Authorization: `Bearer ${token()}`,
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    const data = response.status === 204 ? null : await response.json().catch(() => null);

    if (!response.ok) {
      const detail = data?.detail;
      const errorText = Array.isArray(detail)
        ? detail.map((item: { msg?: string }) => item.msg).join(", ")
        : typeof detail === "string"
        ? detail
        : data?.message || "Something went wrong";

      throw new Error(errorText);
    }

    return data;
  }

  function showMessage(text: string, type: "success" | "error" = "success") {
    setMessage(text);
    setMessageType(type);
  }

  async function loadAppointments(currentRole = role) {
    try {
      if (currentRole === "DOCTOR") {
        const data = await request("/appointments/doctor/my");
        setDoctorAppointments(Array.isArray(data) ? data : []);

        try {
          const reportData = await request("/appointments/doctor/weekly-report");
          setWeeklyReport(Array.isArray(reportData?.report) ? reportData.report : []);
        } catch (reportError) {
          setWeeklyReport([]);
          showMessage(
            reportError instanceof Error
              ? `Appointments loaded, but weekly report failed: ${reportError.message}`
              : "Appointments loaded, but weekly report could not be loaded.",
            "error"
          );
        }
      } else {
        const data = await request("/appointments/my");
        setAppointments(Array.isArray(data) ? data : []);
      }
    } catch (error) {
      showMessage(error instanceof Error ? error.message : "Could not load appointments", "error");
    }
  }

  useEffect(() => {
    async function initialize() {
      const savedToken = sessionStorage.getItem("access_token");

      if (!savedToken) {
        router.replace("/login");
        return;
      }

      const currentDate = todayLocalDate();
      setSearchDate(currentDate);
      setTodayDate(currentDate);
      setNowTimestamp(Date.now());

      try {
        const response = await fetch(`${API}/auth/me`, {
          headers: { Authorization: `Bearer ${savedToken}` },
        });

        if (!response.ok) {
          sessionStorage.removeItem("access_token");
          router.replace("/login");
          return;
        }

        const user = await response.json();
        setRole(user.role);
        setEmail(user.email);
        await loadAppointments(user.role);
      } catch {
        showMessage("Could not connect to the server.", "error");
      } finally {
        setLoading(false);
      }
    }

    initialize();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function logout() {
    sessionStorage.removeItem("access_token");
    router.push("/login");
  }

  async function searchDoctors(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setMessage("");

    try {
      const data = await request("/patients/search-doctors", {
        method: "POST",
        body: JSON.stringify({
          specialization,
          appointment_date: searchDate,
        }),
      });

      const list = Array.isArray(data)
        ? data
        : Array.isArray(data?.doctors)
        ? data.doctors
        : [];

      setDoctors(list);
      showMessage(list.length ? `${list.length} doctor(s) found.` : "No doctors or available slots found.");
    } catch (error) {
      showMessage(error instanceof Error ? error.message : "Search failed", "error");
    } finally {
      setBusy(false);
    }
  }

  async function bookAppointment(slotId: number) {
    if (!confirm("Are you sure you want to book this appointment?")) return;

    setBusy(true);
    try {
      await request("/appointments/book", {
        method: "POST",
        body: JSON.stringify({ slot_id: slotId }),
      });

      showMessage("Appointment booked successfully!");
      await loadAppointments("PATIENT");

      if (searchDate) {
        const data = await request("/patients/search-doctors", {
          method: "POST",
          body: JSON.stringify({ specialization, appointment_date: searchDate }),
        });
        setDoctors(Array.isArray(data) ? data : data?.doctors || []);
      }
    } catch (error) {
      showMessage(error instanceof Error ? error.message : "Booking failed", "error");
    } finally {
      setBusy(false);
    }
  }

  async function cancelAppointment(id: number) {
    if (!confirm("Are you sure you want to cancel this appointment?")) return;

    try {
      await request(`/appointments/${id}/cancel`, { method: "PATCH" });
      showMessage("Appointment cancelled successfully!");
      await loadAppointments("PATIENT");
    } catch (error) {
      showMessage(error instanceof Error ? error.message : "Cancellation failed", "error");
    }
  }

  async function rescheduleAppointment(id: number) {
    const newSlotId = rescheduleSlots[id];

    if (!newSlotId) {
      showMessage("Please select a new available slot.", "error");
      return;
    }

    try {
      await request(`/appointments/${id}/reschedule`, {
        method: "PATCH",
        body: JSON.stringify({ new_slot_id: Number(newSlotId) }),
      });

      showMessage("Appointment rescheduled successfully!");
      await loadAppointments("PATIENT");
      setRescheduleSlots((old) => ({ ...old, [id]: "" }));
    } catch (error) {
      showMessage(error instanceof Error ? error.message : "Rescheduling failed", "error");
    }
  }

  async function updateStatus(id: number, status: "COMPLETED" | "NO_SHOW") {
    try {
      await request(`/appointments/${id}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      });

      showMessage(`Appointment marked as ${status.replace("_", " ")}.`);
      await loadAppointments("DOCTOR");
    } catch (error) {
      showMessage(error instanceof Error ? error.message : "Could not update status", "error");
    }
  }

  async function createSlot(e: FormEvent) {
    e.preventDefault();

    if (!slotStart || !slotEnd) {
      showMessage("Please enter both start and end time.", "error");
      return;
    }

    if (new Date(slotEnd) <= new Date(slotStart)) {
      showMessage("End time must be after start time.", "error");
      return;
    }

    try {
      const data = await request("/availability/slots", {
        method: "POST",
        body: JSON.stringify({
          start_time: slotStart,
          end_time: slotEnd,
        }),
      });

      showMessage(`Availability slot created successfully! Slot ID: ${data.slot_id}`);
      setSlotStart("");
      setSlotEnd("");
    } catch (error) {
      showMessage(error instanceof Error ? error.message : "Could not create slot", "error");
    }
  }

  async function deleteSlot(e: FormEvent) {
    e.preventDefault();

    if (!deleteSlotId) {
      showMessage("Please enter a slot ID.", "error");
      return;
    }

    if (!confirm(`Delete availability slot ${deleteSlotId}?`)) return;

    try {
      await request(`/availability/slots/${deleteSlotId}`, { method: "DELETE" });
      showMessage("Availability slot deleted successfully!");
      setDeleteSlotId("");
    } catch (error) {
      showMessage(error instanceof Error ? error.message : "Could not delete slot", "error");
    }
  }

  const patientBooked = appointments.filter((a) => a.status === "BOOKED").length;
  const patientCompleted = appointments.filter((a) => a.status === "COMPLETED").length;
  const doctorBooked = doctorAppointments.filter((a) => a.status === "BOOKED").length;
  const doctorCompleted = doctorAppointments.filter((a) => a.status === "COMPLETED").length;

  const todayAppointmentCount = doctorAppointments.filter(
    (a) => a.start_time.slice(0, 10) === todayDate
  ).length;

  const upcomingAppointments = doctorAppointments
    .filter((a) => a.status === "BOOKED" && new Date(a.start_time).getTime() > nowTimestamp)
    .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())
    .slice(0, 5);

  function reportCount(status: string) {
    return weeklyReport.find((item) => item.status === status)?.appointment_count ?? 0;
  }

  const styles = {
    page: {
      minHeight: "100vh",
      background: "#f4f7fb",
      color: "#172554",
      fontFamily: "Arial, sans-serif",
    } as const,
    header: {
      background: "#ffffff",
      borderBottom: "1px solid #e2e8f0",
      padding: "16px 5%",
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      flexWrap: "wrap" as const,
      gap: 12,
    },
    brand: { fontSize: 24, fontWeight: 800, color: "#155eef" },
    main: { maxWidth: 1200, margin: "auto", padding: "30px 20px" },
    card: {
      background: "#ffffff",
      border: "1px solid #e5eaf2",
      borderRadius: 16,
      padding: 22,
      boxShadow: "0 4px 16px rgba(15, 23, 42, 0.04)",
    },
    button: {
      background: "#155eef",
      color: "#ffffff",
      border: 0,
      borderRadius: 9,
      padding: "11px 17px",
      fontWeight: 700,
      cursor: "pointer",
    },
    input: {
      width: "100%",
      boxSizing: "border-box" as const,
      padding: 12,
      border: "1px solid #cbd5e1",
      borderRadius: 9,
      fontSize: 14,
      background: "#ffffff",
      color: "#172554",
    },
    muted: { color: "#64748b", fontSize: 13 },
  };

  if (loading) {
    return (
      <div style={{ ...styles.page, display: "grid", placeItems: "center" }}>
        <div style={{ textAlign: "center" }}>
          <h2 style={{ color: "#155eef" }}>ClinicCare</h2>
          <p>Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (!role) {
    return (
      <div style={{ ...styles.page, padding: 40, textAlign: "center" }}>
        <h2>Unable to load dashboard</h2>
        <p>Please check that your backend server is running.</p>
        <button style={styles.button} onClick={() => router.push("/login")}>Go to Login</button>
      </div>
    );
  }

  const isDoctor = role === "DOCTOR";

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <div style={styles.brand}>✚ ClinicCare</div>

        <div style={{ display: "flex", alignItems: "center", gap: 15, flexWrap: "wrap" }}>
          <div style={{ textAlign: "right" }}>
            <div style={{ fontWeight: 700, fontSize: 14 }}>{email}</div>
            <div style={styles.muted}>{isDoctor ? "Doctor Account" : "Patient Account"}</div>
          </div>
          <button
            onClick={logout}
            style={{ ...styles.button, background: "#eff6ff", color: "#155eef" }}
          >
            Logout
          </button>
        </div>
      </header>

      <main style={styles.main}>
        <section
          style={{
            background: "linear-gradient(120deg, #155eef, #397cf6)",
            borderRadius: 20,
            padding: "30px",
            color: "#ffffff",
            marginBottom: 25,
          }}
        >
          <div style={{ fontSize: 13, opacity: 0.85, marginBottom: 8 }}>
            {isDoctor ? "DOCTOR WORKSPACE" : "PATIENT WORKSPACE"}
          </div>
          <h1 style={{ fontSize: 29, margin: "0 0 10px" }}>
            {isDoctor ? "Welcome to your Doctor Dashboard" : "Your health, our priority."}
          </h1>
          <p style={{ margin: 0, opacity: 0.9, lineHeight: 1.6 }}>
            {isDoctor
              ? "Manage your appointments, update patient visits and manage your availability."
              : "Find doctors, book appointments and manage your healthcare in one place."}
          </p>
        </section>

        {message && (
          <div
            style={{
              padding: 14,
              borderRadius: 10,
              marginBottom: 20,
              background: messageType === "error" ? "#fee2e2" : "#dcfce7",
              color: messageType === "error" ? "#991b1b" : "#166534",
              border: `1px solid ${messageType === "error" ? "#fecaca" : "#bbf7d0"}`,
              fontSize: 14,
            }}
          >
            {message}
            <button
              onClick={() => setMessage("")}
              style={{ float: "right", border: 0, background: "transparent", cursor: "pointer", color: "inherit" }}
            >
              ✕
            </button>
          </div>
        )}

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))",
            gap: 16,
            marginBottom: 25,
          }}
        >
          {(isDoctor
            ? [
                { label: "Total Appointments", value: doctorAppointments.length, icon: "📋" },
                { label: "Today's Appointments", value: todayAppointmentCount, icon: "☀️" },
                { label: "Upcoming / Booked", value: doctorBooked, icon: "📅" },
                { label: "Completed Visits", value: doctorCompleted, icon: "✓" },
                { label: "No-show Visits", value: doctorAppointments.filter((a) => a.status === "NO_SHOW").length, icon: "⚠️" },
              ]
            : [
                { label: "Total Appointments", value: appointments.length, icon: "📋" },
                { label: "Active Bookings", value: patientBooked, icon: "📅" },
                { label: "Completed Visits", value: patientCompleted, icon: "✓" },
                { label: "Cancelled", value: appointments.filter((a) => a.status === "CANCELLED").length, icon: "↩" },
              ]
          ).map((item) => (
            <div key={item.label} style={styles.card}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: 25 }}>{item.icon}</span>
                <span style={{ fontSize: 28, fontWeight: 800, color: "#155eef" }}>{item.value}</span>
              </div>
              <div style={{ color: "#64748b", fontSize: 13, marginTop: 12 }}>{item.label}</div>
            </div>
          ))}
        </div>

        {!isDoctor && (
          <section style={{ ...styles.card, marginBottom: 25 }}>
            <div style={{ marginBottom: 18 }}>
              <h2 style={{ margin: "0 0 6px", fontSize: 21 }}>Find your doctor</h2>
              <p style={styles.muted}>Search by specialization and appointment date.</p>
            </div>

            <form
              onSubmit={searchDoctors}
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))",
                gap: 14,
                alignItems: "end",
              }}
            >
              <label style={{ fontSize: 13, fontWeight: 700 }}>
                Specialization
                <select
                  value={specialization}
                  onChange={(e) => setSpecialization(e.target.value)}
                  style={{ ...styles.input, marginTop: 7 }}
                >
                  <option value="General">General</option>
                  <option value="Cardiology">Cardiology</option>
                  <option value="Dermatology">Dermatology</option>
                  <option value="Neurology">Neurology</option>
                  <option value="Pediatrics">Pediatrics</option>
                  <option value="Orthopedics">Orthopedics</option>
                  <option value="Gynecology">Gynecology</option>
                </select>
              </label>

              <label style={{ fontSize: 13, fontWeight: 700 }}>
                Appointment Date
                <input
                  type="date"
                  min={searchDate || undefined}
                  value={searchDate}
                  onChange={(e) => setSearchDate(e.target.value)}
                  style={{ ...styles.input, marginTop: 7 }}
                  required
                />
              </label>

              <button type="submit" disabled={busy} style={styles.button}>
                {busy ? "Searching..." : "⌕ Search Doctors"}
              </button>
            </form>

            {doctors.length > 0 && (
              <div style={{ marginTop: 25 }}>
                <h3 style={{ fontSize: 17, marginBottom: 15 }}>Available Doctors</h3>

                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 15 }}>
                  {doctors.map((doctor) => (
                    <div
                      key={doctor.doctor_id}
                      style={{
                        border: "1px solid #e2e8f0",
                        borderRadius: 13,
                        padding: 18,
                        background: "#fbfdff",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 15 }}>
                        <div
                          style={{
                            width: 48,
                            height: 48,
                            borderRadius: "50%",
                            background: "#dbeafe",
                            color: "#155eef",
                            display: "grid",
                            placeItems: "center",
                            fontSize: 23,
                          }}
                        >
                          ⚕
                        </div>
                        <div>
                          <div style={{ fontWeight: 800 }}>{doctor.name}</div>
                          <div style={styles.muted}>{doctor.specialization}</div>
                        </div>
                      </div>

                      <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 10 }}>
                        Available time slots
                      </div>

                      {doctor.available_slots?.length ? (
                        <div style={{ display: "grid", gap: 9 }}>
                          {doctor.available_slots.map((slot) => (
                            <div
                              key={slot.slot_id}
                              style={{
                                background: "#eff6ff",
                                borderRadius: 9,
                                padding: 10,
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "center",
                                gap: 8,
                                flexWrap: "wrap",
                              }}
                            >
                              <div style={{ fontSize: 12, color: "#1e40af" }}>
                                {formatTime(slot.start_time)} – {formatTime(slot.end_time)}
                              </div>
                              <button
                                onClick={() => bookAppointment(slot.slot_id)}
                                disabled={busy}
                                style={{ ...styles.button, padding: "8px 12px", fontSize: 12 }}
                              >
                                Book
                              </button>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p style={styles.muted}>No available slots for this doctor.</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        )}

        {isDoctor && (
          <>
            <section style={{ ...styles.card, marginBottom: 25 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, flexWrap: "wrap", marginBottom: 18 }}>
                <div>
                  <h2 style={{ margin: "0 0 6px", fontSize: 21 }}>Weekly appointment report</h2>
                  <p style={styles.muted}>Summary of your appointments for the current week.</p>
                </div>
                <button
                  onClick={() => loadAppointments("DOCTOR")}
                  style={{ ...styles.button, background: "#eff6ff", color: "#155eef" }}
                >
                  ↻ Refresh report
                </button>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 12 }}>
                {[
                  { label: "Booked", value: reportCount("BOOKED"), color: "#1d4ed8", bg: "#dbeafe" },
                  { label: "Completed", value: reportCount("COMPLETED"), color: "#15803d", bg: "#dcfce7" },
                  { label: "Cancelled", value: reportCount("CANCELLED"), color: "#b91c1c", bg: "#fee2e2" },
                  { label: "No-show", value: reportCount("NO_SHOW"), color: "#92400e", bg: "#fef3c7" },
                ].map((item) => (
                  <div key={item.label} style={{ background: item.bg, borderRadius: 12, padding: 16 }}>
                    <div style={{ fontSize: 25, fontWeight: 800, color: item.color }}>{item.value}</div>
                    <div style={{ fontSize: 13, fontWeight: 700, color: item.color, marginTop: 5 }}>{item.label}</div>
                  </div>
                ))}
              </div>
            </section>

            <section style={{ ...styles.card, marginBottom: 25 }}>
              <h2 style={{ margin: "0 0 6px", fontSize: 21 }}>Upcoming appointments</h2>
              <p style={styles.muted}>Your next five booked patient visits.</p>

              {upcomingAppointments.length === 0 ? (
                <p style={{ ...styles.muted, marginTop: 18 }}>You have no upcoming booked appointments.</p>
              ) : (
                <div style={{ display: "grid", gap: 11, marginTop: 17 }}>
                  {upcomingAppointments.map((a) => (
                    <div
                      key={a.appointment_id}
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        gap: 12,
                        flexWrap: "wrap",
                        border: "1px solid #e2e8f0",
                        borderRadius: 11,
                        padding: 14,
                      }}
                    >
                      <div>
                        <div style={{ fontWeight: 800 }}>{a.patient_name}</div>
                        <div style={styles.muted}>Appointment #{a.appointment_id}</div>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <div style={{ fontWeight: 700, fontSize: 13 }}>{formatDate(a.start_time)}</div>
                        <div style={styles.muted}>{formatTime(a.start_time)} – {formatTime(a.end_time)}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </>
        )}

        {isDoctor && (
          <section style={{ ...styles.card, marginBottom: 25 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
              <div>
                <h2 style={{ margin: "0 0 6px", fontSize: 21 }}>Manage availability</h2>
                <p style={styles.muted}>Create appointment slots for your patients.</p>
              </div>
              <span style={{ fontSize: 28 }}>🗓️</span>
            </div>

            <form
              onSubmit={createSlot}
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))",
                gap: 14,
                alignItems: "end",
                marginTop: 18,
              }}
            >
              <label style={{ fontSize: 13, fontWeight: 700 }}>
                Start Date & Time
                <input
                  type="datetime-local"
                  value={slotStart}
                  onChange={(e) => setSlotStart(e.target.value)}
                  style={{ ...styles.input, marginTop: 7 }}
                  required
                />
              </label>

              <label style={{ fontSize: 13, fontWeight: 700 }}>
                End Date & Time
                <input
                  type="datetime-local"
                  value={slotEnd}
                  onChange={(e) => setSlotEnd(e.target.value)}
                  style={{ ...styles.input, marginTop: 7 }}
                  required
                />
              </label>

              <button type="submit" style={styles.button}>＋ Create Slot</button>
            </form>

            <div style={{ borderTop: "1px solid #e2e8f0", margin: "22px 0" }} />

            <h3 style={{ fontSize: 16 }}>Delete an availability slot</h3>
            <form onSubmit={deleteSlot} style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
              <input
                type="number"
                min="1"
                placeholder="Enter Slot ID"
                value={deleteSlotId}
                onChange={(e) => setDeleteSlotId(e.target.value)}
                style={{ ...styles.input, maxWidth: 250 }}
                required
              />
              <button type="submit" style={{ ...styles.button, background: "#dc2626" }}>
                Delete Slot
              </button>
            </form>
          </section>
        )}

        <section style={styles.card}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, flexWrap: "wrap", marginBottom: 20 }}>
            <div>
              <h2 style={{ margin: "0 0 6px", fontSize: 21 }}>
                {isDoctor ? "Patient appointments" : "My appointments"}
              </h2>
              <p style={styles.muted}>
                {isDoctor ? "Review visits and update appointment status." : "View and manage your bookings."}
              </p>
            </div>
            <button
              onClick={() => loadAppointments()}
              style={{ ...styles.button, background: "#eff6ff", color: "#155eef" }}
            >
              ↻ Refresh
            </button>
          </div>

          {isDoctor ? (
            doctorAppointments.length === 0 ? (
              <div style={{ textAlign: "center", padding: 35, color: "#64748b" }}>
                <div style={{ fontSize: 38 }}>📅</div>
                <h3>No appointments yet</h3>
                <p style={styles.muted}>Patient bookings will appear here.</p>
              </div>
            ) : (
              <div style={{ display: "grid", gap: 13 }}>
                {doctorAppointments.map((a) => (
                  <div key={a.appointment_id} style={{ border: "1px solid #e2e8f0", borderRadius: 12, padding: 17 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
                      <div>
                        <div style={{ fontWeight: 800, fontSize: 16 }}>{a.patient_name}</div>
                        <div style={styles.muted}>Appointment ID: {a.appointment_id}</div>
                      </div>
                      <span style={{ ...statusStyle(a.status), padding: "6px 11px", borderRadius: 20, fontSize: 12, fontWeight: 800, height: "fit-content" }}>
                        {a.status.replace("_", " ")}
                      </span>
                    </div>

                    <div style={{ background: "#f8fafc", borderRadius: 9, padding: 12, marginTop: 13, fontSize: 13, lineHeight: 1.9 }}>
                      <div>📅 <strong>{formatDate(a.start_time)}</strong></div>
                      <div>🕒 {formatTime(a.start_time)} – {formatTime(a.end_time)}</div>
                    </div>

                    {a.status === "BOOKED" && (
                      <div style={{ display: "flex", gap: 9, marginTop: 13, flexWrap: "wrap" }}>
                        <button
                          onClick={() => updateStatus(a.appointment_id, "COMPLETED")}
                          style={{ ...styles.button, background: "#16a34a" }}
                        >
                          ✓ Mark Completed
                        </button>
                        <button
                          onClick={() => updateStatus(a.appointment_id, "NO_SHOW")}
                          style={{ ...styles.button, background: "#d97706" }}
                        >
                          Mark No Show
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )
          ) : (
            appointments.length === 0 ? (
              <div style={{ textAlign: "center", padding: 35, color: "#64748b" }}>
                <div style={{ fontSize: 38 }}>🩺</div>
                <h3>No appointments yet</h3>
                <p style={styles.muted}>Search for a doctor to book your first appointment.</p>
              </div>
            ) : (
              <div style={{ display: "grid", gap: 13 }}>
                {appointments.map((a) => (
                  <div key={a.appointment_id} style={{ border: "1px solid #e2e8f0", borderRadius: 12, padding: 17 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
                      <div>
                        <div style={{ fontWeight: 800, fontSize: 16 }}>{a.doctor_name}</div>
                        <div style={styles.muted}>{a.specialization} · Appointment #{a.appointment_id}</div>
                      </div>
                      <span style={{ ...statusStyle(a.status), padding: "6px 11px", borderRadius: 20, fontSize: 12, fontWeight: 800, height: "fit-content" }}>
                        {a.status.replace("_", " ")}
                      </span>
                    </div>

                    <div style={{ background: "#f8fafc", borderRadius: 9, padding: 12, marginTop: 13, fontSize: 13, lineHeight: 1.9 }}>
                      <div>📅 <strong>{formatDate(a.start_time)}</strong></div>
                      <div>🕒 {formatTime(a.start_time)} – {formatTime(a.end_time)}</div>
                      <div>🆔 Slot ID: {a.slot_id}</div>
                    </div>

                    {a.status === "BOOKED" && (
                      <div style={{ display: "flex", gap: 9, marginTop: 13, flexWrap: "wrap", alignItems: "center" }}>
                        <button
                          onClick={() => cancelAppointment(a.appointment_id)}
                          style={{ ...styles.button, background: "#dc2626" }}
                        >
                          Cancel Appointment
                        </button>

                        <select
                          value={rescheduleSlots[a.appointment_id] || ""}
                          onChange={(e) => setRescheduleSlots((old) => ({ ...old, [a.appointment_id]: e.target.value }))}
                          style={{ ...styles.input, maxWidth: 190 }}
                        >
                          <option value="">Select new slot ID</option>
                          {doctors.flatMap((doctor) => doctor.available_slots || []).map((slot) => (
                            <option key={slot.slot_id} value={slot.slot_id}>
                              Slot {slot.slot_id} · {formatDate(slot.start_time)} · {formatTime(slot.start_time)}
                            </option>
                          ))}
                        </select>

                        <button
                          onClick={() => rescheduleAppointment(a.appointment_id)}
                          style={styles.button}
                        >
                          Reschedule
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )
          )}
        </section>

        <footer style={{ textAlign: "center", color: "#94a3b8", fontSize: 12, padding: "28px 0 5px" }}>
          © 2026 ClinicCare · Your Health, Our Priority
        </footer>
      </main>
    </div>
  );
}
