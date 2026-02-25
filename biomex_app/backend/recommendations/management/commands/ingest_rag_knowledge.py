from django.core.management.base import BaseCommand, CommandError

from recommendations.rag_service import BiomexRAGService, RAGConfigurationError, RAGServiceError


class Command(BaseCommand):
    help = "Ingest knowledge into Pinecone for BiomeX RAG chatbot."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            default="nutrition_db",
            choices=["nutrition_db", "csv"],
            help="Knowledge source type.",
        )
        parser.add_argument(
            "--namespace",
            default="",
            help="Override Pinecone namespace.",
        )
        parser.add_argument(
            "--csv-path",
            default="",
            help="Path to CSV file when source=csv.",
        )
        parser.add_argument(
            "--csv-text-column",
            default="",
            help="Optional CSV column to use as text body.",
        )

    def handle(self, *args, **options):
        source = options["source"]
        namespace = (options.get("namespace") or "").strip() or None
        csv_path = (options.get("csv_path") or "").strip() or None
        csv_text_column = (options.get("csv_text_column") or "").strip() or None

        service = BiomexRAGService()
        try:
            result = service.ingest_knowledge(
                source=source,
                namespace=namespace,
                csv_path=csv_path,
                csv_text_column=csv_text_column,
            )
        except (RAGConfigurationError, RAGServiceError) as exc:
            raise CommandError(str(exc))

        self.stdout.write(
            self.style.SUCCESS(
                f"Ingestion terminée: {result['ingested_count']} chunks dans namespace '{result['namespace']}'"
            )
        )
