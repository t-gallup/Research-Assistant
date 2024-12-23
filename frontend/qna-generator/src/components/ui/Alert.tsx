import * as React from "react";
import { cn } from "./lib/utils";

const Alert = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { variant?: "destructive" }
>(({ className, variant, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "rounded-lg border p-4",
      variant === "destructive"
        ? "border-destructive bg-destructive text-destructive-foreground"
        : "border-muted-foreground bg-muted-foreground text-muted-foreground",
      className
    )}
    {...props}
  />
));
Alert.displayName = "Alert";

const AlertTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement> & { children: React.ReactNode }
>(({ className, children, ...props }, ref) => (
  <h3 ref={ref} className={cn("text-lg font-semibold", className)} {...props}>
    {children}
  </h3>
));
AlertTitle.displayName = "AlertTitle";

const AlertDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p ref={ref} className={cn("text-sm", className)} {...props} />
));
AlertDescription.displayName = "AlertDescription";

export { Alert, AlertTitle, AlertDescription };
