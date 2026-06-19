/**
 * Flag — inlined circular country/region flag SVGs.
 *
 * Flag artwork sourced from circle-flags (MIT License, © HatScripts):
 * https://github.com/HatScripts/circle-flags
 * Each entry below is the inner content of that project's `flags/{code}.svg`
 * (512×512, circular via a clip mask), inlined here so the app needs no build
 * plugin and ships zero runtime fetches. Mask ids were namespaced per code
 * (`a` -> `flag-{code}`) so multiple flags can render on one page without
 * colliding DOM ids.
 *
 * Codes available: kr, us, cn, jp, eu (see src/lib/flags.ts for FLAG_CODES).
 */
import type { FlagCode } from "@/lib/flags";

export interface FlagProps {
  code: FlagCode;
  /** Pixel size for both width and height. Defaults to 20. */
  size?: number;
  className?: string;
  /** Accessible label. When provided the flag is exposed to assistive tech; otherwise it is decorative (aria-hidden). */
  title?: string;
}

/**
 * Inner SVG content (everything between <svg> and </svg>) for each supported
 * flag, keyed by ISO-style code. Verbatim from circle-flags except mask ids,
 * which were rewritten from `a` to `flag-<code>` for uniqueness.
 */
const FLAG_SVGS: Record<FlagCode, string> = {
  kr: '<mask id="flag-kr"><circle cx="256" cy="256" r="256" fill="#fff"/></mask><g mask="url(#flag-kr)"><path fill="#eee" d="M0 0h512v512H0Z"/><path fill="#333" d="m350 335 24-24 16 16-24 23zm-39 39 24-24 15 16-23 24zm87 8 23-24 16 16-24 24zm-40 39 24-23 16 15-24 24Zm16-63 24-23 15 15-23 24zm-39 40 23-24 16 16-24 23zm63-221-63-63 15-15 64 63zm-63-15-24-24 16-16 23 24zm39 39-24-24 16-15 24 23zm8-87-24-23 16-16 24 24Zm39 40-23-24 15-16 24 24ZM91 358l63 63-16 16-63-63zm63 16 23 24-15 15-24-23zm-40-39 24 23-16 16-23-24zm24-24 63 63-16 16-63-63zm16-220-63 63-16-16 63-63zm23 23-63 63-15-16 63-63zm24 24-63 63-16-16 63-63z"/><path fill="#d80027" d="M319 319 193 193a89 89 0 1 1 126 126z"/><path fill="#0052b4" d="M319 319a89 89 0 1 1-126-126z"/><circle cx="224.5" cy="224.5" r="44.5" fill="#d80027"/><circle cx="287.5" cy="287.5" r="44.5" fill="#0052b4"/></g>',
  us: '<mask id="flag-us"><circle cx="256" cy="256" r="256" fill="#fff"/></mask><g mask="url(#flag-us)"><path fill="#eee" d="M256 0h256v64l-32 32 32 32v64l-32 32 32 32v64l-32 32 32 32v64l-256 32L0 448v-64l32-32-32-32v-64z"/><path fill="#d80027" d="M224 64h288v64H224Zm0 128h288v64H256ZM0 320h512v64H0Zm0 128h512v64H0Z"/><path fill="#0052b4" d="M0 0h256v256H0Z"/><path fill="#eee" d="m187 243 57-41h-70l57 41-22-67zm-81 0 57-41H93l57 41-22-67zm-81 0 57-41H12l57 41-22-67zm162-81 57-41h-70l57 41-22-67zm-81 0 57-41H93l57 41-22-67zm-81 0 57-41H12l57 41-22-67Zm162-82 57-41h-70l57 41-22-67Zm-81 0 57-41H93l57 41-22-67zm-81 0 57-41H12l57 41-22-67Z"/></g>',
  cn: '<mask id="flag-cn"><circle cx="256" cy="256" r="256" fill="#fff"/></mask><g mask="url(#flag-cn)"><path fill="#d80027" d="M0 0h512v512H0z"/><path fill="#ffda44" d="m140.1 155.8 22.1 68h71.5l-57.8 42.1 22.1 68-57.9-42-57.9 42 22.2-68-57.9-42.1H118zm163.4 240.7-16.9-20.8-25 9.7 14.5-22.5-16.9-20.9 25.9 6.9 14.6-22.5 1.4 26.8 26 6.9-25.1 9.6zm33.6-61 8-25.6-21.9-15.5 26.8-.4 7.9-25.6 8.7 25.4 26.8-.3-21.5 16 8.6 25.4-21.9-15.5zm45.3-147.6L370.6 212l19.2 18.7-26.5-3.8-11.8 24-4.6-26.4-26.6-3.8 23.8-12.5-4.6-26.5 19.2 18.7zm-78.2-73-2 26.7 24.9 10.1-26.1 6.4-1.9 26.8-14.1-22.8-26.1 6.4 17.3-20.5-14.2-22.7 24.9 10.1z"/></g>',
  jp: '<mask id="flag-jp"><circle cx="256" cy="256" r="256" fill="#fff"/></mask><g mask="url(#flag-jp)"><path fill="#eee" d="M0 0h512v512H0z"/><circle cx="256" cy="256" r="111.3" fill="#d80027"/></g>',
  eu: '<mask id="flag-eu"><circle cx="256" cy="256" r="256" fill="#fff"/></mask><g mask="url(#flag-eu)"><path fill="#0052b4" d="M0 0h512v512H0z"/><path fill="#ffda44" d="m256 100.2 8.3 25.5H291l-21.7 15.7 8.3 25.6-21.7-15.8-21.7 15.8 8.3-25.6-21.7-15.7h26.8zm-110.2 45.6 24 12.2 18.9-19-4.2 26.5 23.9 12.2-26.5 4.2-4.2 26.5-12.2-24-26.5 4.3 19-19zM100.2 256l25.5-8.3V221l15.7 21.7 25.6-8.3-15.8 21.7 15.8 21.7-25.6-8.3-15.7 21.7v-26.8zm45.6 110.2 12.2-24-19-18.9 26.5 4.2 12.2-23.9 4.2 26.5 26.5 4.2-24 12.2 4.3 26.5-19-19zM256 411.8l-8.3-25.5H221l21.7-15.7-8.3-25.6 21.7 15.8 21.7-15.8-8.3 25.6 21.7 15.7h-26.8zm110.2-45.6-24-12.2-18.9 19 4.2-26.5-23.9-12.2 26.5-4.2 4.2-26.5 12.2 24 26.5-4.3-19 19zM411.8 256l-25.5 8.3V291l-15.7-21.7-25.6 8.3 15.8-21.7-15.8-21.7 25.6 8.3 15.7-21.7v26.8zm-45.6-110.2-12.2 24 19 18.9-26.5-4.2-12.2 23.9-4.2-26.5-26.5-4.2 24-12.2-4.3-26.5 19 19z"/></g>',
};

/** Escape the five XML special chars so a caller-supplied title can't inject markup. */
function escapeXml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

/**
 * Renders an inlined circular flag for the given country/region code.
 * Pass `title` for an accessible name; omit it for a purely decorative flag.
 *
 * The SVG body comes only from the closed, vetted FLAG_SVGS record (keyed by a
 * type-checked FlagCode), and the caller-supplied `title` is XML-escaped before
 * being embedded, so dangerouslySetInnerHTML carries no untrusted markup.
 */
export function Flag({ code, size = 20, className, title }: FlagProps) {
  const inner = FLAG_SVGS[code];
  const a11y = title
    ? { role: "img" as const, "aria-label": title }
    : { "aria-hidden": true as const };

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 512 512"
      className={className}
      {...a11y}
      dangerouslySetInnerHTML={{
        __html: title ? `<title>${escapeXml(title)}</title>${inner}` : inner,
      }}
    />
  );
}

export default Flag;
