output "namespace" {
  description = "Kubernetes namespace"
  value       = kubernetes_namespace.model_drift.metadata[0].name
}

output "api_service_name" {
  description = "API service name"
  value       = kubernetes_service_v1.drift_api_service.metadata[0].name
}

output "dashboard_service_name" {
  description = "Dashboard service name"
  value       = kubernetes_service_v1.drift_dashboard_service.metadata[0].name
}

output "dashboard_nodeport" {
  description = "Dashboard NodePort"
  value       = var.dashboard_nodeport
}