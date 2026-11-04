package study;
import jakarta.servlet.http.*;
import java.io.IOException;

public class SessionServlet extends HttpServlet {
    @Override protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        req.setCharacterEncoding("UTF-8");
        if ("/logout".equals(req.getPathInfo())) {
            HttpSession current = req.getSession(false);
            if (current != null) current.invalidate();
            resp.setStatus(303);
            resp.setHeader("Location", req.getContextPath() + "/auth/profile");
            return;
        }
        if (!"/login".equals(req.getPathInfo())) { resp.sendError(404); return; }
        // 로컬 학습용 고정 자격 증명이며 실서비스 인증에 사용하지 않습니다.
        if (!"learner".equals(req.getParameter("user")) || !"demo-only".equals(req.getParameter("password"))) {
            resp.sendError(401); return;
        }
        HttpSession session = req.getSession();
        req.changeSessionId();
        session.setMaxInactiveInterval(1200);
        session.setAttribute("loginUser", "learner");
        resp.setStatus(303);
        resp.setHeader("Location", req.getContextPath() + "/auth/profile");
    }
    @Override protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        HttpSession session = req.getSession(false);
        if (session == null || session.getAttribute("loginUser") == null) { resp.sendError(401); return; }
        resp.setContentType("text/plain;charset=UTF-8");
        resp.getWriter().print(session.getAttribute("loginUser"));
    }
}
