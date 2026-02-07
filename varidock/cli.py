from pathlib import Path

import click

from varidock.config import VARIDOCK_CONFIG_DIR, VARIDOCK_CONFIG_FILE


@click.group()
def cli():
    """VariDock - Molecular docking pipeline."""
    pass


@cli.command()
def setup():
    """Interactive setup wizard."""
    VARIDOCK_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    lines = []

    click.echo("=== VariDock Setup ===\n")
    click.echo(
        "Leave blank to skip. You can always edit ~/.varidock/config.toml later.\n"
    )

    # AF3
    click.echo("-- AlphaFold3 --")
    af3_fields = {
        "sif_path": "AF3 Singularity image (.sif)",
        "model_dir": "AF3 model directory",
        "db_dir": "AF3 database directory",
        "runner_script": "AF3 runner script (.py)",
    }
    af3_lines = []
    for key, desc in af3_fields.items():
        val = click.prompt(f"  {desc}", default="", show_default=False)
        if val:
            path = Path(val).expanduser().resolve()
            if not path.exists():
                click.echo(f"    ⚠ Warning: {path} does not exist")
            af3_lines.append(f'{key} = "{path}"')

    if af3_lines:
        lines.append("[af3]")
        lines.extend(af3_lines)
        lines.append("")

    # DeepSurf
    click.echo("\n-- DeepSurf --")
    ds_model = click.prompt(
        "  DeepSurf model directory", default="", show_default=False
    )
    if ds_model:
        path = Path(ds_model).expanduser().resolve()
        if not path.exists():
            click.echo(f"    ⚠ Warning: {path} does not exist")
        lines.append("[deepsurf]")
        lines.append(f'model_dir = "{path}"')
        lines.append("")

    if lines:
        VARIDOCK_CONFIG_FILE.write_text("\n".join(lines) + "\n")
        click.echo(f"\n✓ Config written to {VARIDOCK_CONFIG_FILE}")
    else:
        click.echo("\nNo config to write. You can set env vars instead.")


@cli.command()
def check():
    """Verify that all configured paths exist."""
    from varidock.config import VaridockConfig

    config = VaridockConfig.load()
    all_good = True

    for section_name, section in [("af3", config.af3), ("deepsurf", config.deepsurf)]:
        for field_name, value in section.__dict__.items():
            if value is None:
                click.echo(f"  ⚠ {section_name}.{field_name}: not configured")
            elif not value.exists():
                click.echo(f"  ✗ {section_name}.{field_name}: {value} (NOT FOUND)")
                all_good = False
            else:
                click.echo(f"  ✓ {section_name}.{field_name}: {value}")

    if all_good:
        click.echo("\n✓ All configured paths exist.")
    else:
        click.echo("\n✗ Some paths are missing.")
