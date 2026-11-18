import os
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image


def process_mod(mod_dir):
    mod_dir = Path(mod_dir)
    moddesc_path = mod_dir / 'modDesc.xml'
    if not moddesc_path.exists():
        return {
            'status': 'error',
            'error': 'modDesc.xml not found',
            'dir': str(mod_dir),
        }

    try:
        tree = ET.parse(moddesc_path)
        root = tree.getroot()
        icon_elem = root.find('iconFilename')
        if icon_elem is None or not icon_elem.text:
            return {
                'status': 'error',
                'error': 'No <iconFilename> in modDesc.xml',
                'dir': str(mod_dir),
            }

        icon_filename = icon_elem.text.strip()
        icon_path = mod_dir / icon_filename

        if not icon_path.exists():
            # Tentar encontrar qualquer imagem
            candidates = (
                list(mod_dir.glob('*.png'))
                + list(mod_dir.glob('*.jpg'))
                + list(mod_dir.glob('*.dds'))
            )
            if not candidates:
                return {
                    'status': 'error',
                    'error': f'Icon not found: {icon_filename}',
                    'dir': str(mod_dir),
                }
            icon_path = candidates[0]

        return process_icon(icon_path, mod_dir)

    except Exception as e:
        return {'status': 'error', 'error': str(e), 'dir': str(mod_dir)}


def process_icon(icon_path, mod_dir):
    try:
        before_size = os.path.getsize(icon_path)
        img = Image.open(icon_path)
        before_dim = img.size
        before_format = img.format or icon_path.suffix.upper()[1:]

        img = img.convert('RGBA')

        # 1. Resize/Crop to 512x512
        target_size = 512
        if img.width > target_size or img.height > target_size:
            # Resize keeping aspect ratio
            img.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
            # Crop to 512x512
            new_img = Image.new(
                'RGBA', (target_size, target_size), (0, 0, 0, 0)
            )
            offset = (
                (target_size - img.width) // 2,
                (target_size - img.height) // 2,
            )
            new_img.paste(img, offset)
            img = new_img
        elif img.width < target_size or img.height < target_size:
            # Scale without distortion, fill background
            ratio = min(target_size / img.width, target_size / img.height)
            new_w = int(img.width * ratio)
            new_h = int(img.height * ratio)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            new_img = Image.new(
                'RGBA', (target_size, target_size), (0, 0, 0, 0)
            )
            offset = ((target_size - new_w) // 2, (target_size - new_h) // 2)
            new_img.paste(img, offset)
            img = new_img

        mod_name = mod_dir.name
        dds_out = mod_dir / f'icon_{mod_name}.dds'
        png_out = mod_dir / 'icon.png'

        # Save PNG
        img_rgb = img
        if not any(a != 255 for _, _, _, a in img.getdata()):
            img_rgb = img.convert('RGB')
        img_rgb.save(png_out, 'PNG', optimize=True, compress_level=9)

        # Save DDS (uncompressed for now since Pillow doesn't do DXT5 natively)
        # In a real scenario, we'd call texconv.exe or use a specific C-extension here.
        img.save(dds_out, 'DDS')

        after_dim = (512, 512)
        after_format = 'PNG/DDS'
        after_size = os.path.getsize(png_out) + os.path.getsize(dds_out)

        return {
            'status': 'success',
            'file': icon_path.name,
            'before_dim': before_dim,
            'after_dim': after_dim,
            'before_format': before_format,
            'after_format': after_format,
            'before_size': before_size,
            'after_size': after_size,
            'dir': str(mod_dir),
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e), 'dir': str(mod_dir)}


def run_batch(target_path):
    target_path = Path(target_path)
    results = []

    if (target_path / 'modDesc.xml').exists():
        results.append(process_mod(target_path))
    else:
        for sub in target_path.iterdir():
            if sub.is_dir() and (sub / 'modDesc.xml').exists():
                results.append(process_mod(sub))

    success = sum(1 for r in results if r['status'] == 'success')
    errors = sum(1 for r in results if r['status'] == 'error')

    print('\n--- Resultados ---')
    for r in results:
        if r['status'] == 'success':
            print(f'[OK] {r["dir"]}')
            print(f'     Arquivo: {r["file"]}')
            print(
                f'     Dimensões: {r["before_dim"][0]}x{r["before_dim"][1]} -> {r["after_dim"][0]}x{r["after_dim"][1]}'
            )
            print(f'     Formato: {r["before_format"]} -> {r["after_format"]}')
            print(
                f'     Tamanho: {r["before_size"] / 1024:.1f}KB -> {r["after_size"] / 1024:.1f}KB'
            )
        else:
            print(f'[ERRO] {r["dir"]} - {r.get("error", "Erro desconhecido")}')

    print('\n--- Resumo ---')
    print(f'Total processados: {len(results)}')
    print(f'Sucesso: {success}')
    print(f'Erros: {errors}')
