// frontend/src/utils/dateFormatter.js

/**
 * Format datetime string for display
 * Handles ISO format from backend: "YYYY-MM-DDTHH:MM:SS"
 */
export const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return "-";

  try {
    let date;

    // Handle ISO format with T separator (YYYY-MM-DDTHH:MM:SS)
    if (typeof dateTimeString === "string" && dateTimeString.includes("T")) {
      const [datePart, timePart] = dateTimeString.split("T");
      const [year, month, day] = datePart.split("-");
      const [hours, minutes] = timePart.split(":");

      if (!year || !month || !day || !hours || !minutes) {
        console.error("Invalid date format:", dateTimeString);
        return "Invalid Date";
      }

      // Create date object (month is 0-indexed in JS)
      date = new Date(
        parseInt(year),
        parseInt(month) - 1,
        parseInt(day),
        parseInt(hours),
        parseInt(minutes),
      );
    }
    // Handle space-separated format "YYYY-MM-DD HH:MM:SS" (fallback)
    else if (
      typeof dateTimeString === "string" &&
      dateTimeString.includes(" ")
    ) {
      const [datePart, timePart] = dateTimeString.split(" ");
      const [year, month, day] = datePart.split("-");
      const [hours, minutes] = timePart.split(":");

      if (!year || !month || !day || !hours || !minutes) {
        console.error("Invalid date format:", dateTimeString);
        return "Invalid Date";
      }

      date = new Date(
        parseInt(year),
        parseInt(month) - 1,
        parseInt(day),
        parseInt(hours),
        parseInt(minutes),
      );
    }
    // Handle Date object
    else if (dateTimeString instanceof Date) {
      date = dateTimeString;
    }
    // Fallback: try to parse as-is
    else {
      date = new Date(dateTimeString);
    }

    // Check if date is valid
    if (isNaN(date.getTime())) {
      console.error("Invalid date value:", dateTimeString);
      return "Invalid Date";
    }

    // Format date parts
    const monthNames = [
      "Jan",
      "Feb",
      "Mar",
      "Apr",
      "May",
      "Jun",
      "Jul",
      "Aug",
      "Sep",
      "Oct",
      "Nov",
      "Dec",
    ];

    const dateStr = `${monthNames[date.getMonth()]} ${String(date.getDate()).padStart(2, "0")}, ${date.getFullYear()}`;

    // Format time (12-hour format)
    const hours = date.getHours();
    const hour12 = hours % 12 || 12;
    const ampm = hours >= 12 ? "PM" : "AM";
    const timeStr = `${hour12}:${String(date.getMinutes()).padStart(2, "0")} ${ampm}`;

    return `${dateStr}, ${timeStr}`;
  } catch (err) {
    console.error("Date formatting error:", err, dateTimeString);
    return "Invalid Date";
  }
};

/**
 * Format just the date part (no time)
 */
export const formatDate = (dateString) => {
  if (!dateString) return "-";

  try {
    let date;

    if (dateString.includes("T")) {
      const [datePart] = dateString.split("T");
      const [year, month, day] = datePart.split("-");
      date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
    } else if (dateString.includes(" ")) {
      const [datePart] = dateString.split(" ");
      const [year, month, day] = datePart.split("-");
      date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
    } else {
      const [year, month, day] = dateString.split("-");
      date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
    }

    if (isNaN(date.getTime())) {
      console.error("Invalid date:", dateString);
      return "Invalid Date";
    }

    const monthNames = [
      "Jan",
      "Feb",
      "Mar",
      "Apr",
      "May",
      "Jun",
      "Jul",
      "Aug",
      "Sep",
      "Oct",
      "Nov",
      "Dec",
    ];

    return `${monthNames[date.getMonth()]} ${date.getDate()}, ${date.getFullYear()}`;
  } catch (err) {
    console.error("Date formatting error:", err, dateString);
    return "Invalid Date";
  }
};

/**
 * Parse datetime string and return Date object
 * Used for date comparisons
 */
export const parseDateTime = (dateTimeString) => {
  if (!dateTimeString) return null;

  try {
    if (dateTimeString.includes("T")) {
      const [datePart, timePart] = dateTimeString.split("T");
      const [year, month, day] = datePart.split("-");
      const [hours, minutes] = timePart.split(":");

      return new Date(
        parseInt(year),
        parseInt(month) - 1,
        parseInt(day),
        parseInt(hours),
        parseInt(minutes),
      );
    } else if (dateTimeString.includes(" ")) {
      const [datePart, timePart] = dateTimeString.split(" ");
      const [year, month, day] = datePart.split("-");
      const [hours, minutes] = timePart.split(":");

      return new Date(
        parseInt(year),
        parseInt(month) - 1,
        parseInt(day),
        parseInt(hours),
        parseInt(minutes),
      );
    }

    return new Date(dateTimeString);
  } catch (err) {
    console.error("Date parsing error:", err, dateTimeString);
    return null;
  }
};

/**
 * Check if a datetime has passed (for prescription writing validation)
 */
export const hasDateTimePassed = (dateTimeString) => {
  const date = parseDateTime(dateTimeString);
  if (!date) return false;

  const now = new Date();
  return now >= date;
};

/**
 * Get time status for display (upcoming, ready, expired)
 */
export const getTimeStatus = (dateTimeString) => {
  const date = parseDateTime(dateTimeString);

  if (!date || isNaN(date.getTime())) {
    return { status: "error", message: "Invalid date" };
  }

  const now = new Date();
  const diffMs = date - now;
  const diffHours = Math.abs(Math.floor(diffMs / (1000 * 60 * 60)));

  if (diffMs > 0) {
    return { status: "upcoming", message: `In ${diffHours} hours` };
  } else if (diffMs > -7 * 24 * 60 * 60 * 1000) {
    return { status: "ready", message: `${diffHours} hours ago` };
  } else {
    return { status: "expired", message: "More than 7 days ago" };
  }
};
