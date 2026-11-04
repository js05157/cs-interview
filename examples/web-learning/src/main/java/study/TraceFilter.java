package study;
import jakarta.servlet.*;
import jakarta.servlet.annotation.WebFilter;
import jakarta.servlet.http.*;
import java.io.IOException;

@WebFilter(urlPatterns="/*", dispatcherTypes=DispatcherType.REQUEST)
public class TraceFilter extends HttpFilter {
    @Override protected void doFilter(HttpServletRequest req, HttpServletResponse resp,
                                      FilterChain chain) throws IOException, ServletException {
        resp.setHeader("X-Learning-Filter", "applied");
        long start = System.nanoTime();
        try { chain.doFilter(req, resp); }
        finally { getServletContext().log("request elapsed(ns)=" + (System.nanoTime() - start)); }
    }
}
