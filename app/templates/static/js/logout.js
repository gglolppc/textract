async function handleLogout(e) {
  e.preventDefault();
  try {
    const res = await fetch("/auth/logout", {
      method: "GET",
      credentials: "include"
    });
    if (res.redirected) {
      window.location.href = res.url;
    } else {
      window.location.href = "/";
    }
  } catch (err) {
    console.error("Logout failed:", err);
  }
}

// Навесим обработчик на все элементы с data-action="logout"
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('[data-action="logout"]').forEach(el => {
    el.addEventListener("click", handleLogout);
  });
});
