STYLE_PRESETS = {
    'Photorealistic': {
        'positive_suffix': '8k architectural photograph of a real building, photorealistic render, award winning architecture, architectural digest magazine cover, professional DSLR photography, sharp focus, high detail, realistic materials, concrete walls, glass windows, wooden doors, tiled roof, real world building, unreal engine 5, octane render, V-Ray render',
        'negative': 'blurry, deformed, low quality, warped walls, broken geometry, cartoon, anime, painting, sketch, watermark, ugly, distorted, bad proportions, text, logo, abstract, surreal, fantasy, people, faces, animals'
    },
    'Brutalism': {
        'positive_suffix': 'brutalist architecture building, exposed raw concrete structure, heavy geometric block forms, harsh dramatic shadows, monolithic concrete walls, modernist building exterior, real world brutalist building photograph, 8k architectural render',
        'negative': 'blurry, deformed, low quality, colorful, decorative, ornate, wood, warm colors, cartoon, sketch, abstract, fantasy, people, faces, animals'
    },
    'Minimalist': {
        'positive_suffix': 'minimalist house interior design, clean straight lines, white plastered walls, polished concrete floor, natural light through large windows, Scandinavian house design, simple geometric rooms, real house interior, architectural digest, 8k render',
        'negative': 'blurry, deformed, clutter, busy, decorative, ornate, cartoon, sketch, dark, abstract, fantasy, people, faces, animals'
    },
    'Biophilic': {
        'positive_suffix': 'biophilic house design, living green walls on building facade, natural materials, indoor plants, wooden beams, stone cladding, organic architectural forms, natural light through skylights, sustainable eco-friendly house, real building photograph, 8k render',
        'negative': 'blurry, deformed, synthetic, plastic, cartoon, sketch, abstract, fantasy, people, faces, animals'
    },
    'Industrial': {
        'positive_suffix': 'industrial loft house interior, exposed steel pipes and ductwork, metal I-beams, red brick walls, Edison bulb lighting, polished concrete floor, warehouse conversion into living space, real building interior photograph, 8k architectural render',
        'negative': 'blurry, deformed, clean white, cartoon, sketch, low quality, abstract, fantasy, people, faces, animals'
    },
    'Art Deco': {
        'positive_suffix': 'art deco building interior, geometric wall patterns, gold and brass accents, luxury marble flooring, symmetrical architectural design, 1920s glamour hotel lobby, ornate ceiling moldings, real building interior, architectural digest, 8k render',
        'negative': 'blurry, deformed, minimalist, brutalist, cartoon, sketch, low quality, abstract, fantasy, people, faces, animals'
    },
    'Futuristic': {
        'positive_suffix': 'futuristic house architecture, parametric facade design, curved glass surfaces, smart glass panels, embedded LED strip lighting, sci-fi inspired building interior, Zaha Hadid inspired real building, white smooth walls, real architectural photograph, 8k render, unreal engine 5',
        'negative': 'blurry, deformed, traditional, rustic, cartoon, sketch, low quality, abstract, fantasy, people, faces, animals'
    }
}

SKETCH_MODE_STRUCTURAL_ENFORCER = 'real house architecture, building interior with walls ceiling and floor, precise geometry, clean structural lines, straight walls, defined room layout, architectural blueprint accuracy, real world construction, doors and windows, building structure'

def build_sketch_prompt(user_prompt: str, style_preset: str) -> tuple[str, str]:
    """Returns (full_positive_prompt, full_negative_prompt) for sketch mode"""
    preset = STYLE_PRESETS.get(style_preset, STYLE_PRESETS['Photorealistic'])
    
    pos = f"{user_prompt}, {SKETCH_MODE_STRUCTURAL_ENFORCER}, {preset['positive_suffix']}"
    neg = preset['negative']
    
    return pos.strip(", "), neg

def build_text_prompt(user_prompt: str, style_preset: str) -> tuple[str, str]:
    """Returns (full_positive_prompt, full_negative_prompt) for text mode"""
    preset = STYLE_PRESETS.get(style_preset, STYLE_PRESETS['Photorealistic'])
    
    pos = f"{user_prompt}, {preset['positive_suffix']}"
    neg = preset['negative']
    
    return pos.strip(", "), neg
