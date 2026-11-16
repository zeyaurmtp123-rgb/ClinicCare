
export default function Home() {
  return (
    <main className="min-h-screen bg-blue-50">
      {/* Navigation Bar */}
      <nav className="flex items-center justify-between bg-white px-8 py-5 shadow-sm">
        <h1 className="text-2xl font-bold text-blue-700">
          ClinicCare
        </h1>

        <div className="flex gap-4">
          <a
            href="/login"
            className="rounded-lg border border-blue-600 px-5 py-2 text-blue-600 hover:bg-blue-50"
          >
            Login
          </a>

          <a
            href="/register"
            className="rounded-lg bg-blue-600 px-5 py-2 text-white hover:bg-blue-700"
          >
            Register
          </a>
        </div>
      </nav>

      {/* Main Section */}
      <section className="flex min-h-[75vh] flex-col items-center justify-center px-6 text-center">
        <h2 className="mb-5 max-w-3xl text-4xl font-bold text-gray-800 md:text-6xl">
          Your Health, Our Priority
        </h2>

        <p className="mb-8 max-w-xl text-lg text-gray-600">
          Book appointments with doctors easily.
          Find available time slots and manage your appointments
          in one place.
        </p>

        <a
          href="/login"
          className="rounded-lg bg-blue-600 px-8 py-3 text-lg font-semibold text-white shadow hover:bg-blue-700"
        >
          Book an Appointment
        </a>
      </section>

      {/* Features */}
      <section className="grid gap-6 px-8 pb-16 md:grid-cols-3">
        <div className="rounded-xl bg-white p-7 text-center shadow-sm">
          <h3 className="mb-3 text-xl font-bold text-blue-700">
            Find Doctors
          </h3>
          <p className="text-gray-600">
            Search doctors by their specialization.
          </p>
        </div>

        <div className="rounded-xl bg-white p-7 text-center shadow-sm">
          <h3 className="mb-3 text-xl font-bold text-blue-700">
            Book Appointments
          </h3>
          <p className="text-gray-600">
            Choose an available slot and book easily.
          </p>
        </div>

        <div className="rounded-xl bg-white p-7 text-center shadow-sm">
          <h3 className="mb-3 text-xl font-bold text-blue-700">
            Manage Appointments
          </h3>
          <p className="text-gray-600">
            View and manage your appointments.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white py-5 text-center text-gray-500">
        © 2026 ClinicCare. All rights reserved.
      </footer>
    </main>
  );
}
