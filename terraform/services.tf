resource "kubernetes_service_v1" "drift_api_service" {
  metadata {
    name      = "drift-api-service"
    namespace = kubernetes_namespace.model_drift.metadata[0].name

    labels = {
      app = "drift-api"
    }
  }

  spec {
    selector = {
      app = "drift-api"
    }

    port {
      port        = var.api_port
      target_port = var.api_port
      protocol    = "TCP"
    }

    type = "ClusterIP"
  }
}

resource "kubernetes_service_v1" "drift_dashboard_service" {
  metadata {
    name      = "drift-dashboard-service"
    namespace = kubernetes_namespace.model_drift.metadata[0].name

    labels = {
      app = "drift-dashboard"
    }
  }

  spec {
    selector = {
      app = "drift-dashboard"
    }

    port {
      port        = var.dashboard_port
      target_port = var.dashboard_port
      node_port   = var.dashboard_nodeport
      protocol    = "TCP"
    }

    type = "NodePort"
  }
}