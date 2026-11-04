package study;
import jakarta.servlet.http.*;
import java.io.IOException;

public class CookieServlet extends HttpServlet {
    @Override protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        if ("/set".equals(req.getPathInfo()) || "/delete".equals(req.getPathInfo())) {
            Cookie cookie = new Cookie("recent", "4");
            cookie.setPath(req.getContextPath());
            cookie.setHttpOnly(true);
            cookie.setAttribute("SameSite", "Lax");
            cookie.setMaxAge("/delete".equals(req.getPathInfo()) ? 0 : 90);
            resp.addCookie(cookie);
        }
        String value = "absent";
        if (req.getCookies() != null) for (Cookie c : req.getCookies())
            if ("recent".equals(c.getName())) value = c.getValue();
        resp.setContentType("text/plain;charset=UTF-8");
        resp.getWriter().print(value);
    }
}
