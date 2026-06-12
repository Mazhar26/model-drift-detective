resource "kubernetes_namespace" "model_drift" {
  metadata {
    name = var.namespace_name
  }
}