export interface Route {
  routes: string[]
  label: string
}

export interface UserInfo {
  id: number
  username: string
  email?: string
  name?: string
  lastName?: string
  applicationName: string
}

export interface Camera {
  id: number
  name: string
  status: string
  location_lat: number
  location_lng: number
}

export interface Alert {
  id: number
  status: string
  location_lat: number
  location_lng: number
  details: string
  camera_id: number
  camera: Camera
}