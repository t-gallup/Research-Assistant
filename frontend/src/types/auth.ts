export interface User {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;
}
  
export interface AuthContextType {
  user: User | null;
  loading: boolean;
  error?: string | null;
}