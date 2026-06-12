resource "kubernetes_deployment_v1" "drift_api" {
  metadata {
    name      = "drift-api"
    namespace = kubernetes_namespace.model_drift.metadata[0].name

    labels = {
      app = "drift-api"
    }
  }

  spec {
    replicas = var.replica_count

    selector {
      match_labels = {
        app = "drift-api"
      }
    }

    template {
      metadata {
        labels = {
          app = "drift-api"
        }
      }

      spec {
        volume {
          name = "logs-volume"

          empty_dir {}
        }

        container {
          name              = "api"
          image             = "drift-api:latest"
          image_pull_policy = "IfNotPresent"

          port {
            container_port = var.api_port
          }

          env_from {
            config_map_ref {
              name = kubernetes_config_map.drift_detective_config.metadata[0].name
            }
          }

          env {
            name  = "API_HOST"
            value = "0.0.0.0"
          }

          env {
            name  = "API_PORT"
            value = "8000"
          }


          volume_mount {
            name       = "logs-volume"
            mount_path = "/app/logs"
          }
        }
      }
    }
  }
}

resource "kubernetes_deployment_v1" "drift_dashboard" {
  metadata {
    name      = "drift-dashboard"
    namespace = kubernetes_namespace.model_drift.metadata[0].name

    labels = {
      app = "drift-dashboard"
    }
  }

  spec {
    replicas = var.replica_count

    selector {
      match_labels = {
        app = "drift-dashboard"
      }
    }

    template {
      metadata {
        labels = {
          app = "drift-dashboard"
        }
      }

      spec {
        volume {
          name = "logs-volume"

          empty_dir {}
        }

        container {
          name              = "dashboard"
          image             = "drift-dashboard:latest"
          image_pull_policy = "IfNotPresent"

          port {
            container_port = var.dashboard_port
          }

          env_from {
            config_map_ref {
              name = kubernetes_config_map.drift_detective_config.metadata[0].name
            }
          }

          env {
            name  = "API_HOST"
            value = "drift-api-service"
          }

          env {
            name  = "API_PORT"
            value = "8000"
          }

          env {
            name  = "STREAMLIT_PORT"
            value = "8501"
          }

          volume_mount {
            name       = "logs-volume"
            mount_path = "/app/logs"
          }
        }
      }
    }
  }
}