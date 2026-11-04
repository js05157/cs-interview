package study;
import jakarta.servlet.*;
import jakarta.servlet.http.*;
import java.io.IOException;
import java.util.List;

public class LessonServlet extends HttpServlet {
    public static class Member {
        private final String name;
        public Member(String name) { this.name = name; }
        public String getName() { return name; }
    }
    @Override protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException, ServletException {
        req.setAttribute("message", "요청에서 전달한 값");
        req.setAttribute("members", List.of(new Member("Ada"), new Member("<script>demo</script>")));
        req.getRequestDispatcher("/WEB-INF/views/members.jsp").forward(req, resp);
    }
}
