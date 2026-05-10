import Nav from "@/components/Nav";
import Hero from "@/components/Hero";
import RawData from "@/components/RawData";
import Cleaning from "@/components/Cleaning";
import FeatureSelection from "@/components/FeatureSelection";
import Personas from "@/components/Personas";
import PerClusterDrivers from "@/components/PerClusterDrivers";
import Predictor from "@/components/Predictor";
import MarketingPlan from "@/components/MarketingPlan";
import Footer from "@/components/Footer";

export default function Page() {
  return (
    <main className="relative">
      <Nav />
      <Hero />
      <RawData />
      <Cleaning />
      <FeatureSelection />
      <Personas />
      <PerClusterDrivers />
      <Predictor />
      <MarketingPlan />
      <Footer />
    </main>
  );
}
