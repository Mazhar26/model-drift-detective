resource "kubernetes_namespace" "model_drift"{
    metadata{
        name = "model-drift"
    }
}

resource "kubernetes_config_map" "drift_detective_config" {
  metadata {
    name      = "drift-detective-config"
    namespace = kubernetes_namespace.model_drift.metadata[0].name

    labels = {
      app = "model-drift-detective"
    }
  }

  data = {
    DEFAULT_THRESHOLD        = "0.1"
    P_VALUE_THRESHOLD        = "0.05"
    SEVERITY_HIGH_THRESHOLD  = "0.3"
    SEVERITY_MEDIUM_THRESHOLD = "0.1"
    LOG_LEVEL                = "INFO"
    MODEL_N_ESTIMATORS       = "100"
    MODEL_RANDOM_STATE       = "42"
    ALERTS_ENABLED           = "false"
  }
}

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
      port        = 8000
      target_port = 8000
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
      port        = 8501
      target_port = 8501
      node_port   = 30085
      protocol    = "TCP"
    }

    type = "NodePort"
  }
}

resource "kubernetes_deployment_v1" "drift_api" {
  metadata {
    name      = "drift-api"
    namespace = kubernetes_namespace.model_drift.metadata[0].name

    labels = {
      app = "drift-api"
    }
  }

  spec {
    replicas = 1

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
            container_port = 8000
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
    replicas = 1

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
            container_port = 8501
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