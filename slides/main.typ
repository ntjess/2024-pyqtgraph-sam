#import "@local/doc-templates:0.1.0": tv-slides
#import "@preview/showman:0.1.0": formatter
#import "@local/toolbox:0.1.0": shadow-box
#import tv-slides: *
#import "@preview/cetz:0.2.1": canvas, draw
#import "@preview/based:0.1.0": base64

#show: template.with(theme: "dark")
#show raw.where(block: false): it => box(
  pad(y: -0.35em, x: -0.17em, formatter.format-raw(inline: true, it))
)

#let media(path, ..args) = image("media/" + path, ..args)
#let shadow-media(path, ..args, image-args: (:)) = shadow-image(media(path, ..image-args), ..args)
#let vid(uri: none, title: none, ..args) = {
  linked-video(shadow-media(..args), uri: uri, title: title)
}

#let embed-svg(svg-text, replace-path) = {
  let fmt = replace-path.split(".").last()
  let data = base64.encode(read(replace-path, encoding: none))
  let to-replace = "data:image/" + fmt + ";base64," + data
  svg-text.replace(replace-path, to-replace)
}


#title-slide-2[
  #title[
    Annotationem ex Nihilo
    #set text(weight: "regular")
    #set block(spacing: 0em)
    #fit-to-width(100%)[Image annotation from scratch using `PyQtGraph` and `FastSAM`]
  ]

  #author[
    #set text(tv-gold)
    Nathan Jessurun\
    Founder, TerraVerum
  ]
]

// #let _old-slide = slide
// #let slide(..args) = {
//   set page(background: image("media/background.svg"))
//   _old-slide(..args)
// }
#let multi-slide(title, ..body) = slide[
  #heading(title)
  #swap(..body)
]

#multi-slide[Introduction][
  Several types of annotation, most time consuming and informative is #pos[instance segmentation]
  #set align(center + bottom)
  #shadow-media("types-of-annotation.jpg", height: 2.75in)
][
  But #neg[ヽ༼ ಠ_ಠ༽ﾉ detailed annotation is time consuming!]
  #set align(center + bottom)
  #vid(
    uri: "media/unassisted-annotation-timelapse.mp4",
    title: [(manual timelapse)],
    "annotation-thumbnail.jpg",
    height: 3in,
  )
][
  Assistance tools help, but are often #neg[paywalled], #neg[perform poorly], or expect #neg[detailed project workflows]

  #set align(center + bottom)
  #locate(loc => {
    let theme = palette-state.at(loc).theme
    let path = "pricing-" + theme + ".jpg"
    let img = shadow-media(path, height: 2.5in)
    let overlay = read("media/pricing-overlay.svg")
    let replace-str = if theme != "dark" {
      "media/pricing-light.jpg"
    } else {
      "media/pricing-dark.jpg"
    }
    overlay = overlay.replace("pricing-dark.jpg", replace-str)
    overlay = embed-svg(overlay, replace-str)
    col-grid(
      shadow-image(image.decode(overlay), height: 2.5in),
      vid(
        uri: "media/sam-pretrained-2.mp4",
        title: [(Pretrained SAM)],
        "sam-thumbnail.jpg",
        height: 2.5in,
      )
      
    )
  })

]

#slide[
  = Tutorial Components

  + Create a window that loads an image from a file
  + Segment the current image using `FastSAM`
  + Enable object-by-object adjustments
  + Save annotations and edit history
  + Enable manual adjustments using a brush
  + Future work: incorporate metadata & postprocessing
]

#let full-image-slide(title, body) = slide({
  heading(title)
  if body.has("text") {
    body = body.text
  }
  set align(center + bottom)
  if type(body) == str {
    body = shadow-media(body, height: 4.1in, radius: 5pt)
  }
  body
})

#full-image-slide[Window Loading an Image][window-loading-image.jpg]

#full-image-slide[Predictions using Ultralytics `FastSAM`][fast-sam.jpg]

#full-image-slide[Enabling User-Specified Regions][
  #vid(
    uri: "media/region-builder.mp4",
    "region-builder-thumbnail.jpg",
    height: 4.1in,
  )
]

#let todo(title) = full-image-slide(title)[
  #set align(horizon)
  #text(3em)[]
]

#todo[Persisting User Edits]
#todo[Enabling Brush Adjustments]

#slide[
  = Future Work
  Regions are only part of the story. We also need: 

  #let swap-ims(..paths) = swap(
    ..paths.pos().map(
      shadow-media.with(height: 3.3in, image-args: (fit: "contain"))
    )
  )

  #let bodies = (
    (
      heading: pos[Metadata],
      body: [
        (class, tags, comments, ...)
      ]
    ),
    (
      heading: pos[Postprocessing],
      body: [(Filtering, grouping, ...)]
    ),
    (
      heading: pos[Annotation management],
      body: [(copy/delete, bulk edits, ...)]
    )
  )
  #col-grid(columns: (1fr, 0.5fr),
    emph-one-by-one(overview: false, ..bodies),
    swap-ims("sample-annotation.jpg", "postprocessing.jpg", "annotation-management.jpg"),
  )
]

#slide[
  = Future Work
  These are available within #link("https://github.com/TerraVerum/s3a")[S3A]: an open-source labeling tool

  #col-grid[
    #show raw.where(lang: "py"): formatter.format-raw.with(line-numbers: true, fill: none)
    Integrate `FastSAM` (or any algorithm you wish) in #pos[3\* lines of code!]
    ```python
    def wrap_fast_sam(image: np.ndarray):
      label_mask = fast_sam(image)
      return dict(labels=label_mask)
    ```
  ][
    #shadow-media("s3a-window.jpg", height: 3in)
  ]
]

#todo[Conclusion]