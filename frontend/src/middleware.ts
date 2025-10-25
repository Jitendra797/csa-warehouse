import { getToken } from "next-auth/jwt";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { checkRole } from "./lib/roles";

export async function middleware(req: NextRequest) {
  // Skip middleware for static assets and API routes
  if (
    req.nextUrl.pathname.startsWith("/_next") ||
    req.nextUrl.pathname.startsWith("/api") ||
    req.nextUrl.pathname.includes(".js") ||
    req.nextUrl.pathname.includes(".css") ||
    req.nextUrl.pathname.includes(".ico") ||
    req.nextUrl.pathname.includes(".png") ||
    req.nextUrl.pathname.includes(".jpg") ||
    req.nextUrl.pathname.includes(".jpeg") ||
    req.nextUrl.pathname.includes(".gif") ||
    req.nextUrl.pathname.includes(".svg")
  ) {
    return NextResponse.next();
  }

  const token = await getToken({ req });
  const currentPath = req.nextUrl.pathname;
  console.log("[middleware] Current Path:", currentPath);

  // If no token, redirect to login
  if (!token || !token.apiToken) {
    console.log("[middleware] No auth token - redirecting to login", {
      hasToken: Boolean(token),
      hasAccessToken: Boolean(token?.apiToken),
      currentPath,
    });
    return NextResponse.redirect(new URL("/api/auth/signin", req.url));
  }

  try {
    // Check access for the current path
    const accessObject = await checkRole(token.apiToken as string, currentPath);
    console.log("[middleware] Access check result:", accessObject);

    if (!accessObject) {
      console.log(
        "[middleware] No access permissions found - redirecting to access restricted",
      );
      return NextResponse.redirect(new URL("/access-restricted", req.url));
    }

    // Allow access if user has any of the required permissions
    if (accessObject.viewer || accessObject.contributor || accessObject.admin) {
      const response = NextResponse.next();
      response.headers.set("x-user-permissions", JSON.stringify(accessObject));
      return response;
    }

    // If no permissions found, redirect to access restricted page
    return NextResponse.redirect(new URL("/access-restricted", req.url));
  } catch (error) {
    console.error("[middleware] Error checking access:", error, {
      currentPath,
      hasAccessToken: Boolean(token?.apiToken),
    });
    return NextResponse.redirect(new URL("/access-restricted", req.url));
  }
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/datastore/:path*",
    "/pipeline/:path*", 
    "/usermanagement/:path*",
    "/settings/:path*"
  ],
};
