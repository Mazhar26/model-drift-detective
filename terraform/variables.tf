variable "namespace_name" {
  description = "Kubernetes namespace"
  type        = string
}

variable "replica_count" {
  description = "Number of application replicas"
  type        = number
}

variable "api_port" {
  description = "FastAPI service port"
  type        = number
}

variable "dashboard_port" {
  description = "Dashboard service port"
  type        = number
}

variable "dashboard_nodeport" {
  description = "NodePort exposed for dashboard"
  type        = number
}